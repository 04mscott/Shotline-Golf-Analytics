-- Golf tracker schema (PostgreSQL)
-- Conventions: every table has an integer `id` PK unless it is a pure child/junction table.
-- Units: yardage/length in yards or inches as noted; on-course `distance` is feet on the green, yards everywhere else.
-- =====================================================================
-- Courses
-- =====================================================================
-- A physical golf facility (called `clubs` in the original draft; renamed to avoid
-- colliding with golf clubs in the bag).
CREATE TABLE
    facilities (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name text NOT NULL,
        address text,
        city text,
        state text,
        country char(2) NOT NULL DEFAULT 'US',
        latitude numeric(9, 6),
        longitude numeric(9, 6)
    );

CREATE TABLE
    courses (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        facility_id int NOT NULL REFERENCES facilities (id) ON DELETE CASCADE,
        name text NOT NULL,
        UNIQUE (facility_id, name)
    );

-- One row per tee box per gender rating (the same white tees are rated separately for M and F).
-- Total yards / par / hole count are derived from `holes`, so they are not stored here.
CREATE TABLE
    tees (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        course_id int NOT NULL REFERENCES courses (id) ON DELETE CASCADE,
        name text NOT NULL,
        gender char(1) NOT NULL CHECK (gender IN ('M', 'F')),
        course_rating numeric(4, 1) NOT NULL,
        slope_rating smallint NOT NULL CHECK (slope_rating BETWEEN 55 AND 155),
        UNIQUE (course_id, name, gender)
    );

CREATE TABLE
    holes (
        tee_id int NOT NULL REFERENCES tees (id) ON DELETE CASCADE,
        hole_num smallint NOT NULL CHECK (hole_num BETWEEN 1 AND 18),
        par smallint NOT NULL CHECK (par BETWEEN 3 AND 6),
        yardage smallint NOT NULL CHECK (yardage > 0),
        stroke_index smallint NOT NULL CHECK (stroke_index BETWEEN 1 AND 18), -- "handicap" on the scorecard
        PRIMARY KEY (tee_id, hole_num)
    );

-- =====================================================================
-- Users
-- =====================================================================
CREATE TABLE
    users (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name text NOT NULL,
        email text NOT NULL UNIQUE,
        ghin_number text UNIQUE,
        home_course_id int REFERENCES courses (id) ON DELETE SET NULL
    );

-- Estimated handicap index over time, calculated from posted rounds. Current index = latest row.
CREATE TABLE
    handicap_history (
        user_id int NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        effective_on date NOT NULL,
        handicap_index numeric(3, 1) NOT NULL,
        PRIMARY KEY (user_id, effective_on)
    );

-- =====================================================================
-- Equipment
-- =====================================================================
-- Shared by club heads and shafts.
CREATE TABLE
    brands (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name text NOT NULL UNIQUE
    );

-- Catalog of head models. For irons, one row = the whole set (e.g. "T350").
CREATE TABLE
    club_models (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        brand_id int NOT NULL REFERENCES brands (id),
        name text NOT NULL,
        club_type text NOT NULL CHECK (
            club_type IN (
                'driver',
                'fairway_wood',
                'hybrid',
                'iron',
                'wedge',
                'putter'
            )
        ),
        UNIQUE (brand_id, name, club_type)
    );

CREATE TABLE
    shaft_models (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        brand_id int NOT NULL REFERENCES brands (id),
        name text NOT NULL,
        flex text NOT NULL,
        UNIQUE (brand_id, name, flex)
    );

-- One row per physical club you own, with its build specs.
-- Treat a row as immutable: if you reshaft, re-bend or regrip a club, set `retired_on` and
-- insert a new row. Strokes point at this row, so history keeps the specs that were actually used.
-- Adjustments are stored relative to stock (0 = standard) because stock specs differ per club number.
-- `loft` is absolute (needed for gapping) and NULL when unknown/stock.
CREATE TABLE
    bag_clubs (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id int NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        model_id int NOT NULL REFERENCES club_models (id),
        shaft_id int REFERENCES shaft_models (id),
        label text NOT NULL, -- '3 wood', '7 iron', '60 degree'
        loft numeric(3, 1),
        bounce numeric(3, 1),
        length_adj numeric(3, 2) NOT NULL DEFAULT 0, -- inches vs stock
        lie_adj numeric(3, 1) NOT NULL DEFAULT 0, -- degrees vs stock, positive = more upright
        grip text,
        added_on date NOT NULL DEFAULT CURRENT_DATE,
        retired_on date,
        CHECK (
            retired_on IS NULL
            OR retired_on >= added_on
        )
    );

-- Only one active club per label per user.
CREATE UNIQUE INDEX bag_clubs_active_label ON bag_clubs (user_id, label)
WHERE
    retired_on IS NULL;

-- =====================================================================
-- Rounds and strokes
-- =====================================================================
-- `course_id` is not stored: it is always tee -> course.
CREATE TABLE
    rounds (
        id int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        user_id int NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        tee_id int NOT NULL REFERENCES tees (id),
        played_on date NOT NULL,
        holes_played text NOT NULL DEFAULT '18' CHECK (holes_played IN ('18', 'front_9', 'back_9')),
        counts_for_handicap boolean NOT NULL DEFAULT true, -- false for unscored/practice rounds
        -- Handicap snapshot, written when the round is posted. This is historical, not derivable later:
        -- the index in effect on the day sets the net-double-bogey cap used for the differential.
        handicap_index numeric(3, 1),
        differential numeric(4, 1),
        notes text
    );

CREATE INDEX rounds_user_date ON rounds (user_id, played_on);

-- Which clubs were carried in a given round (matters if you swap clubs in and out).
CREATE TABLE
    round_clubs (
        round_id int NOT NULL REFERENCES rounds (id) ON DELETE CASCADE,
        bag_club_id int NOT NULL REFERENCES bag_clubs (id),
        PRIMARY KEY (round_id, bag_club_id)
    );

-- One row per hole played in a round, recording HOW it was entered. `strokes` and `hole_summaries`
-- both reference this row with a composite FK that pins `entry_mode`, so a hole can have stroke rows
-- or a summary row, never both. Insert the round_holes row first, then the child rows.
-- To switch a hole's mode, delete its round_holes row (cascades to its strokes/summary) and re-enter it.
CREATE TABLE
    round_holes (
        round_id int NOT NULL REFERENCES rounds (id) ON DELETE CASCADE,
        hole_num smallint NOT NULL CHECK (hole_num BETWEEN 1 AND 18),
        entry_mode text NOT NULL CHECK (entry_mode IN ('detailed', 'summary')),
        PRIMARY KEY (round_id, hole_num),
        UNIQUE (round_id, hole_num, entry_mode) -- target for the composite FKs below
    );

-- One row per stroke, describing where the ball was when the stroke started.
-- The end position of a stroke is the start of the next one; the last stroke on a hole is the one that holed out.
-- That is all a strokes-gained calculation needs: start lie + distance, the next stroke's start, and penalties.
CREATE TABLE
    strokes (
        round_id int NOT NULL REFERENCES rounds (id) ON DELETE CASCADE,
        hole_num smallint NOT NULL CHECK (hole_num BETWEEN 1 AND 18),
        stroke_num smallint NOT NULL CHECK (stroke_num >= 1),
        lie text NOT NULL CHECK (
            lie IN (
                'tee',
                'fairway',
                'rough',
                'sand',
                'recovery',
                'green'
            )
        ),
        distance int NOT NULL CHECK (distance >= 0), -- to the hole: feet if lie = 'green', else yards
        bag_club_id int REFERENCES bag_clubs (id), -- NULL for unknown club
        -- Result vs target. Both NULL = on target. Two columns so "short and right" is representable.
        miss_lr text CHECK (
            miss_lr IN ('far_left', 'left', 'right', 'far_right')
        ),
        miss_depth text CHECK (miss_depth IN ('short', 'long')),
        -- Cause of a bad strike, if any. NULL = no mistake.
        miss_type text CHECK (
            miss_type IN (
                'push',
                'pull',
                'hook',
                'slice',
                'top',
                'chunk',
                'alignment'
            )
        ),
        -- Penalty strokes caused by THIS stroke (OB, lost ball, water, unplayable). Counts toward score, not stroke_num.
        penalty_strokes smallint NOT NULL DEFAULT 0 CHECK (penalty_strokes >= 0),
        penalty_type text CHECK (
            penalty_type IN (
                'fairway_bunker',
                'greenside_bunker',
                'yellow_penalty_area',
                'red_penalty_area',
                'out_of_bounds'
            )
        ),
        hole_completed boolean NOT NULL DEFAULT true,
        entry_mode text NOT NULL DEFAULT 'detailed' CHECK (entry_mode = 'detailed'),
        PRIMARY KEY (round_id, hole_num, stroke_num),
        FOREIGN KEY (round_id, hole_num, entry_mode) REFERENCES round_holes (round_id, hole_num, entry_mode) ON DELETE CASCADE
    );

CREATE INDEX strokes_club ON strokes (bag_club_id);

CREATE TABLE
    hole_summaries (
        round_id int NOT NULL REFERENCES rounds (id) ON DELETE CASCADE,
        hole_num smallint NOT NULL CHECK (hole_num BETWEEN 1 AND 18),
        score smallint NOT NULL CHECK (score >= 1), -- what goes on the scorecard, penalties included
        putts smallint NOT NULL DEFAULT 0 CHECK (putts >= 0),
        penalty_strokes smallint NOT NULL DEFAULT 0 CHECK (penalty_strokes >= 0),
        hole_completed boolean NOT NULL DEFAULT true,
        entry_mode text NOT NULL DEFAULT 'summary' CHECK (entry_mode = 'summary'),
        PRIMARY KEY (round_id, hole_num),
        FOREIGN KEY (round_id, hole_num, entry_mode) REFERENCES round_holes (round_id, hole_num, entry_mode) ON DELETE CASCADE,
        CHECK (putts + penalty_strokes <= score)
    );

-- =====================================================================
-- Score views (derived, nothing extra to keep in sync)
-- =====================================================================
CREATE VIEW
    detailed_hole_scores AS
WITH
    first_putt AS (
        SELECT
            round_id,
            hole_num,
            MIN(stroke_num) AS n
        FROM
            strokes
        WHERE
            lie = 'green'
        GROUP BY
            round_id,
            hole_num
    )
SELECT
    s.round_id,
    s.hole_num,
    h.par,
    COUNT(*) + SUM(s.penalty_strokes) AS score,
    COUNT(*) FILTER (
        WHERE
            s.lie = 'green'
    ) AS putts,
    -- GIR: on the green (or holed out) in par - 2 strokes or fewer, penalties included.
    CASE
        WHEN fp.n IS NULL THEN COUNT(*) + SUM(s.penalty_strokes) <= h.par - 2
        ELSE fp.n - 1 + COALESCE(
            SUM(s.penalty_strokes) FILTER (
                WHERE
                    s.stroke_num < fp.n
            ),
            0
        ) <= h.par - 2
    END AS gir,
    CASE
        WHEN h.par > 3 THEN COALESCE(
            BOOL_OR (
                s.stroke_num = 2
                AND s.lie IN ('fairway', 'green')
            )
            AND NOT BOOL_OR (
                s.stroke_num = 1
                AND s.penalty_strokes > 0
            ),
            false
        )
    END AS fairway_hit
FROM
    strokes s
    JOIN rounds r ON r.id = s.round_id
    JOIN holes h ON h.tee_id = r.tee_id
    AND h.hole_num = s.hole_num
    LEFT JOIN first_putt fp ON fp.round_id = s.round_id
    AND fp.hole_num = s.hole_num
GROUP BY
    s.round_id,
    s.hole_num,
    h.par,
    fp.n
HAVING
    BOOL_AND (s.hole_completed);

CREATE VIEW
    hole_scores AS
SELECT
    round_id, hole_num, par, score, putts, gir, fairway_hit,
    true AS detailed
FROM
    detailed_hole_scores
UNION ALL
SELECT
    hs.round_id,
    hs.hole_num,
    h.par,
    hs.score,
    hs.putts,
    hs.score - hs.putts <= h.par - 2 AS gir,
    NULL::boolean AS fairway_hit,
    false AS detailed
FROM
    hole_summaries hs
    JOIN rounds r ON r.id = hs.round_id
    JOIN holes h ON h.tee_id = r.tee_id
    AND h.hole_num = hs.hole_num
WHERE
    hs.hole_completed;

CREATE VIEW
    round_scores AS
SELECT
    r.id AS round_id,
    r.user_id,
    r.tee_id,
    r.played_on,
    COUNT(*) AS holes_recorded,
    SUM(hs.score) AS gross_score,
    SUM(hs.score - hs.par) AS to_par,
    SUM(hs.putts) AS putts,
    COUNT(*) FILTER (WHERE hs.gir) AS greens_in_regulation,
    COUNT(hs.gir) AS gir_holes,
    COUNT(*) FILTER (WHERE hs.fairway_hit) AS fairways_hit,
    COUNT(hs.fairway_hit) AS fairway_holes
FROM
    rounds r
    JOIN hole_scores hs ON hs.round_id = r.id
GROUP BY
    r.id;