import logging
import datetime
import os.path
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
print(os.listdir())

def creds ():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())
      return creds
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
      service = build("calendar", "v3", credentials=creds())
      # Call the Calendar API
      now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
      print("Getting the upcoming 10 events")
      events_result = (
          service.events()
          .list(
              calendarId="primary",
              timeMin=now,
              maxResults=10,
              singleEvents=True,
              orderBy="startTime",
          )
          .execute()
      )
      events = events_result.get("items", [])
      
      if not events:
        print("No upcoming events found.")
        return

    # Prints the start and name of the next 10 events
      list_of_events=[]
      for e in events:
         list_of_events.append(e.get("summary"))

      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
      await context.bot.send_message(chat_id=update.effective_chat.id, text=list_of_events)


    except HttpError as error:
      print(f"An error occurred: {error}")


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event_title=update.message.text
    try:
       # create drive api client
       service = build('drive', 'v3', credentials=creds())
       # Create an event object
       event = {
          'summary': event_title,
          'start': {
          'dateTime': datetime.datetime.now().isoformat(),
          'timeZone': 'Asia/Hong_Kong',  # Replace with the desired timezone
        },
        'end': {
            'dateTime': (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'Asia/Hong_Kong',  # Replace with the desired timezone
        },
    }

       # Insert the event into the calendar
       calendar_id = 'primary'  # Use 'primary' for the primary calendar of the authenticated user
       event = service.events().insert(calendarId=calendar_id, body=event).execute()

       # Send a response back to the user
       context.bot.send_message(chat_id=update.effective_chat.id, text='Event added to Google Calendar!')
       
    
    except HttpError as error:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Failure")
        print(F'An error occurred: {error}')
   



 
if __name__ == '__main__':
    application = ApplicationBuilder().token('@@@').build()
    application.add_handler(CommandHandler('start',start))
    application.add_handler(CommandHandler('events',list_events))
    application.add_handler(CommandHandler('addevent',add_event))
    application.run_polling()


    



