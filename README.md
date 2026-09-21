# Golf Data Aanalytics Application

This is a personal project I'm building for personal use to track my golf scores, equipment, and specifically, strokes gained and areas/clubs to prioritize.

## Primary Goals

- Implement a user friendly UI for tracking data at the individual shot level in order to allow real-time tracking during play, without slowing pace of play on the course
- Implement detailed analytics centered around strokes gained using the baseline expected stroke values found [here](https://pinflag.io/tools/expected-strokes-table), able to group by shot type, or even by specific club used
- Track equipment down to minute details, from brand (Titleist, TaylorMade, etc.) to model (GTS2, Qi4D, etc.), even down to the shaft brand, flex, loft and lie angles, etc.
- Implement an LLM chatbot to act as a digital caddie, walking the user through areas of their game that needs work and how to work on it, as well as working through equipment concerns/upgrades, and talking about how a round went or is going

## Current Progress

This application is in the early mock-up stage, primarily existing as a Jupyter notebook where the strokes gained calculation logic currently resides.

### Next Steps

- Develop the PostgreSQL database to store user, course, rounds, and equipment data
- Implement an initial UI to begin integrating the backend logic with user the user facing front end
- Implement advanced analytics features to display strokes gained data, focused around easy to understand visualizations using golf themed graphics, as well as a priority ranking of areas of the users golf game to work on first
- Fully containerize application and eventually deploy in order to use on the course
