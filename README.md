# NVIDIA Volunteer Finder

A Streamlit application to help schedulers find and track volunteers for insider chats.

## Features

- Search for volunteers by CRG, Timezone, and Business Unit
- Display volunteer details (Name, CRG, Timezone, Business Unit, Email)
- Track the number of times each volunteer is selected
- Limit volunteer selections to a maximum of 2 per week
- Automatically open Outlook to schedule volunteers
- Visual statistics on volunteer selection frequency
- NVIDIA-themed UI

## Setup and Installation

1. Ensure you have Python installed (3.7 or newer)
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Data Format

The application uses a CSV file (`volunteers.csv`) with the following columns:
- Insider Volunteers (Name)
- Employee #
- CRG
- Timezone
- Business Unit
- Email

You can modify the CSV file to add, remove, or update volunteers.

## Usage

1. Select filters using the dropdown menus at the top of the page
2. Browse the displayed volunteers (up to 5 matching your criteria)
3. Click the "Schedule" button to select a volunteer
4. The application will open your default email client with a pre-filled email
5. Volunteers who have been selected twice in a week will not appear in search results
6. Selection counts reset automatically every week

## Notes

- Volunteer selection counts are stored in the session state and will reset when the Streamlit server restarts
- The weekly reset is based on the server time 
