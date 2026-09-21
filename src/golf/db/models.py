from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, Boolean, CHAR, CheckConstraint, Column, Date, ForeignKeyConstraint, Identity, Index, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Brands(Base):
    __tablename__ = 'brands'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='brands_pkey'),
        UniqueConstraint('name', name='brands_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    club_models: Mapped[list['ClubModels']] = relationship('ClubModels', back_populates='brand')
    shaft_models: Mapped[list['ShaftModels']] = relationship('ShaftModels', back_populates='brand')


class Facilities(Base):
    __tablename__ = 'facilities'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='facilities_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(CHAR(2), nullable=False, server_default=text("'US'::bpchar"))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(Text)
    state: Mapped[Optional[str]] = mapped_column(Text)
    latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(9, 6))

    courses: Mapped[list['Courses']] = relationship('Courses', back_populates='facility')


t_hole_scores = Table(
    'hole_scores', Base.metadata,
    Column('round_id', Integer),
    Column('hole_num', SmallInteger),
    Column('par', SmallInteger),
    Column('score', BigInteger),
    Column('putts', BigInteger),
    Column('gir', Boolean),
    Column('fairway_hit', Boolean)
)


t_round_scores = Table(
    'round_scores', Base.metadata,
    Column('round_id', Integer),
    Column('user_id', Integer),
    Column('tee_id', Integer),
    Column('played_on', Date),
    Column('holes_recorded', BigInteger),
    Column('gross_score', Numeric),
    Column('to_par', Numeric),
    Column('putts', Numeric),
    Column('greens_in_regulation', BigInteger)
)


class ClubModels(Base):
    __tablename__ = 'club_models'
    __table_args__ = (
        CheckConstraint("club_type = ANY (ARRAY['driver'::text, 'fairway_wood'::text, 'hybrid'::text, 'iron'::text, 'wedge'::text, 'putter'::text])", name='club_models_club_type_check'),
        ForeignKeyConstraint(['brand_id'], ['brands.id'], name='club_models_brand_id_fkey'),
        PrimaryKeyConstraint('id', name='club_models_pkey'),
        UniqueConstraint('brand_id', 'name', 'club_type', name='club_models_brand_id_name_club_type_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    club_type: Mapped[str] = mapped_column(Text, nullable=False)

    brand: Mapped['Brands'] = relationship('Brands', back_populates='club_models')
    bag_clubs: Mapped[list['BagClubs']] = relationship('BagClubs', back_populates='model')


class Courses(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        ForeignKeyConstraint(['facility_id'], ['facilities.id'], ondelete='CASCADE', name='courses_facility_id_fkey'),
        PrimaryKeyConstraint('id', name='courses_pkey'),
        UniqueConstraint('facility_id', 'name', name='courses_facility_id_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    facility_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    facility: Mapped['Facilities'] = relationship('Facilities', back_populates='courses')
    tees: Mapped[list['Tees']] = relationship('Tees', back_populates='course')
    users: Mapped[list['Users']] = relationship('Users', back_populates='home_course')


class ShaftModels(Base):
    __tablename__ = 'shaft_models'
    __table_args__ = (
        ForeignKeyConstraint(['brand_id'], ['brands.id'], name='shaft_models_brand_id_fkey'),
        PrimaryKeyConstraint('id', name='shaft_models_pkey'),
        UniqueConstraint('brand_id', 'name', 'flex', name='shaft_models_brand_id_name_flex_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    flex: Mapped[str] = mapped_column(Text, nullable=False)

    brand: Mapped['Brands'] = relationship('Brands', back_populates='shaft_models')
    bag_clubs: Mapped[list['BagClubs']] = relationship('BagClubs', back_populates='shaft')


class Tees(Base):
    __tablename__ = 'tees'
    __table_args__ = (
        CheckConstraint("gender = ANY (ARRAY['M'::bpchar, 'F'::bpchar])", name='tees_gender_check'),
        CheckConstraint('slope_rating >= 55 AND slope_rating <= 155', name='tees_slope_rating_check'),
        ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE', name='tees_course_id_fkey'),
        PrimaryKeyConstraint('id', name='tees_pkey'),
        UniqueConstraint('course_id', 'name', 'gender', name='tees_course_id_name_gender_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    gender: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    course_rating: Mapped[decimal.Decimal] = mapped_column(Numeric(4, 1), nullable=False)
    slope_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    course: Mapped['Courses'] = relationship('Courses', back_populates='tees')
    holes: Mapped[list['Holes']] = relationship('Holes', back_populates='tee')
    rounds: Mapped[list['Rounds']] = relationship('Rounds', back_populates='tee')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['home_course_id'], ['courses.id'], ondelete='SET NULL', name='users_home_course_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('ghin_number', name='users_ghin_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    ghin_number: Mapped[Optional[str]] = mapped_column(Text)
    home_course_id: Mapped[Optional[int]] = mapped_column(Integer)

    home_course: Mapped[Optional['Courses']] = relationship('Courses', back_populates='users')
    bag_clubs: Mapped[list['BagClubs']] = relationship('BagClubs', back_populates='user')
    handicap_history: Mapped[list['HandicapHistory']] = relationship('HandicapHistory', back_populates='user')
    rounds: Mapped[list['Rounds']] = relationship('Rounds', back_populates='user')


class BagClubs(Base):
    __tablename__ = 'bag_clubs'
    __table_args__ = (
        CheckConstraint('retired_on IS NULL OR retired_on >= added_on', name='bag_clubs_check'),
        ForeignKeyConstraint(['model_id'], ['club_models.id'], name='bag_clubs_model_id_fkey'),
        ForeignKeyConstraint(['shaft_id'], ['shaft_models.id'], name='bag_clubs_shaft_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='bag_clubs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='bag_clubs_pkey'),
        Index('bag_clubs_active_label', 'user_id', 'label', postgresql_where='(retired_on IS NULL)', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    length_adj: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 2), nullable=False, server_default=text('0'))
    lie_adj: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 1), nullable=False, server_default=text('0'))
    added_on: Mapped[datetime.date] = mapped_column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    shaft_id: Mapped[Optional[int]] = mapped_column(Integer)
    loft: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 1))
    bounce: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 1))
    grip: Mapped[Optional[str]] = mapped_column(Text)
    retired_on: Mapped[Optional[datetime.date]] = mapped_column(Date)

    model: Mapped['ClubModels'] = relationship('ClubModels', back_populates='bag_clubs')
    shaft: Mapped[Optional['ShaftModels']] = relationship('ShaftModels', back_populates='bag_clubs')
    user: Mapped['Users'] = relationship('Users', back_populates='bag_clubs')
    round: Mapped[list['Rounds']] = relationship('Rounds', secondary='round_clubs', back_populates='bag_club')
    strokes: Mapped[list['Strokes']] = relationship('Strokes', back_populates='bag_club')


class HandicapHistory(Base):
    __tablename__ = 'handicap_history'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='handicap_history_user_id_fkey'),
        PrimaryKeyConstraint('user_id', 'effective_on', name='handicap_history_pkey')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    effective_on: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    handicap_index: Mapped[decimal.Decimal] = mapped_column(Numeric(3, 1), nullable=False)

    user: Mapped['Users'] = relationship('Users', back_populates='handicap_history')


class Holes(Base):
    __tablename__ = 'holes'
    __table_args__ = (
        CheckConstraint('hole_num >= 1 AND hole_num <= 18', name='holes_hole_num_check'),
        CheckConstraint('par >= 3 AND par <= 6', name='holes_par_check'),
        CheckConstraint('stroke_index >= 1 AND stroke_index <= 18', name='holes_stroke_index_check'),
        CheckConstraint('yardage > 0', name='holes_yardage_check'),
        ForeignKeyConstraint(['tee_id'], ['tees.id'], ondelete='CASCADE', name='holes_tee_id_fkey'),
        PrimaryKeyConstraint('tee_id', 'hole_num', name='holes_pkey')
    )

    tee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hole_num: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    par: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    yardage: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    stroke_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    tee: Mapped['Tees'] = relationship('Tees', back_populates='holes')


class Rounds(Base):
    __tablename__ = 'rounds'
    __table_args__ = (
        CheckConstraint("holes_played = ANY (ARRAY['18'::text, 'front_9'::text, 'back_9'::text])", name='rounds_holes_played_check'),
        ForeignKeyConstraint(['tee_id'], ['tees.id'], name='rounds_tee_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='rounds_user_id_fkey'),
        PrimaryKeyConstraint('id', name='rounds_pkey'),
        Index('rounds_user_date', 'user_id', 'played_on')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    played_on: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    holes_played: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'18'::text"))
    counts_for_handicap: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    handicap_index: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(3, 1))
    differential: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(4, 1))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    bag_club: Mapped[list['BagClubs']] = relationship('BagClubs', secondary='round_clubs', back_populates='round')
    tee: Mapped['Tees'] = relationship('Tees', back_populates='rounds')
    user: Mapped['Users'] = relationship('Users', back_populates='rounds')
    strokes: Mapped[list['Strokes']] = relationship('Strokes', back_populates='round')


t_round_clubs = Table(
    'round_clubs', Base.metadata,
    Column('round_id', Integer, primary_key=True),
    Column('bag_club_id', Integer, primary_key=True),
    ForeignKeyConstraint(['bag_club_id'], ['bag_clubs.id'], name='round_clubs_bag_club_id_fkey'),
    ForeignKeyConstraint(['round_id'], ['rounds.id'], ondelete='CASCADE', name='round_clubs_round_id_fkey'),
    PrimaryKeyConstraint('round_id', 'bag_club_id', name='round_clubs_pkey')
)


class Strokes(Base):
    __tablename__ = 'strokes'
    __table_args__ = (
        CheckConstraint('distance >= 0', name='strokes_distance_check'),
        CheckConstraint('hole_num >= 1 AND hole_num <= 18', name='strokes_hole_num_check'),
        CheckConstraint("lie = ANY (ARRAY['tee'::text, 'fairway'::text, 'rough'::text, 'sand'::text, 'recovery'::text, 'green'::text])", name='strokes_lie_check'),
        CheckConstraint("miss_depth = ANY (ARRAY['short'::text, 'long'::text])", name='strokes_miss_depth_check'),
        CheckConstraint("miss_lr = ANY (ARRAY['far_left'::text, 'left'::text, 'right'::text, 'far_right'::text])", name='strokes_miss_lr_check'),
        CheckConstraint("miss_type = ANY (ARRAY['push'::text, 'pull'::text, 'hook'::text, 'slice'::text, 'top'::text, 'chunk'::text, 'alignment'::text])", name='strokes_miss_type_check'),
        CheckConstraint('penalty_strokes >= 0', name='strokes_penalty_strokes_check'),
        CheckConstraint('stroke_num >= 1', name='strokes_stroke_num_check'),
        ForeignKeyConstraint(['bag_club_id'], ['bag_clubs.id'], name='strokes_bag_club_id_fkey'),
        ForeignKeyConstraint(['round_id'], ['rounds.id'], ondelete='CASCADE', name='strokes_round_id_fkey'),
        PrimaryKeyConstraint('round_id', 'hole_num', 'stroke_num', name='strokes_pkey'),
        Index('strokes_club', 'bag_club_id')
    )

    round_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hole_num: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    stroke_num: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    lie: Mapped[str] = mapped_column(Text, nullable=False)
    distance: Mapped[int] = mapped_column(Integer, nullable=False)
    penalty_strokes: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    bag_club_id: Mapped[Optional[int]] = mapped_column(Integer)
    miss_lr: Mapped[Optional[str]] = mapped_column(Text)
    miss_depth: Mapped[Optional[str]] = mapped_column(Text)
    miss_type: Mapped[Optional[str]] = mapped_column(Text)

    bag_club: Mapped[Optional['BagClubs']] = relationship('BagClubs', back_populates='strokes')
    round: Mapped['Rounds'] = relationship('Rounds', back_populates='strokes')
