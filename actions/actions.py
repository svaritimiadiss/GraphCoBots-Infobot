# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher

# import ruamel.yaml
# import pathlib
from typing import Dict, Text, Any, List
from rasa_sdk.events import SlotSet, ReminderScheduled, ReminderCancelled
import random
# import time
import requests
import datetime
import pytz  # Για να πάρω την σημερινή ώρα
import locale
from actions import utils
import yaml
import os
from dotenv import load_dotenv, set_key
import json

# Load the responses from the JSON file just ONCE
with open('actions/genai_placeholders.yml', 'r', encoding='utf-8') as f:
    genai_data = yaml.safe_load(f)

load_dotenv()

#* Generative service endpoints
GENAI_BASE_URL = os.getenv("FASTAPI_APP_URL")
OPENAI_RESPONSE_ENDPOINT = os.getenv("OPENAI_RESPONSE_ENDPOINT")

#* Vector Store parameters
VECTOR_DB_NAME = genai_data["vector_stores"]["vector_db"]
COLLECTION_NAME = genai_data["vector_stores"]["collection"]

#* Generative models
CHAT_MODEL = genai_data["models"]["chat"]

def get_weather(open_meteo):
    locale.setlocale(locale.LC_ALL, 'el_GR.UTF-8')
    # os.environ["LC_ALL"] = "el_GR.UTF-8"

    # response = requests.get(open_meteo, timeout=30, verify="/etc/ssl/certs/ca-certificates.crt")

    response = requests.get(open_meteo, timeout=30)

    # with requests.Session() as session:
    #     session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0))
    #     response = session.get(open_meteo, verify=False, timeout=30)

    # response = requests.get(open_meteo, verify=False, timeout=30)
    # logging.info(response)
    # logging.info(response.headers)
    # print("response CODE: ", response)
    # print("response Headers: ", response.headers)
    #
    x = response.json()
    # logging.info(x)
    #
    # ΔΕΝ χρειάζεται να μπουν σε λιστα γιατί ειναι ΗΔΗ!!! ΛΟΛ
    weekdays = []
    for weekday in x['forecast']['forecastday']:
        # print("\nweekday!!: ", weekday)
        result = datetime.datetime.strptime(weekday['date'], "%Y-%m-%d")
        weekdays.append(result.weekday())
    #
    # logging.info("Πήρε επιτχυμένα το API")
    return x, weekdays
    # return []


# def wmo_code(code):
#     if code in (0, 1, 2):
#         weather_code = 'καθαρός ουρανός'
#     elif code in (3, 80):
#         weather_code = 'αρκετή συννεφιά'
#     elif code in (45, 48):
#         weather_code = 'ομίχλη'
#     elif code in (51, 53, 56, 61):
#         weather_code = 'ασθενής βροχή'
#     elif code in (55, 57, 63, 66):
#         weather_code = 'βροχή'
#     elif code in (65, 67, 81, 82):
#         weather_code = 'έντονη βροχόπτωση'
#     elif code in (71, 73, 77):
#         weather_code = 'χιόνι'
#     elif code in (75, 85, 86):
#         weather_code = 'έντονη χιονόπτωση'
#     elif code == 95:
#         weather_code = 'καταιγίδα'
#     elif code in (96, 99):
#         weather_code = 'καταιγίδα με χαλάζι'
#
#     print("Πήρε επιτυχημένα το weather code!")
#     return weather_code

def wmo_code(code):
    if code in (1000, 1003):
        weather_code = 'καθαρός ουρανός'
    elif code in (1006, 1009):
        weather_code = 'αρκετή συννεφιά'
    elif code in (1030, 1135, 1147):
        weather_code = 'ομίχλη'
    elif code in (1063, 1069, 1150, 1153, 1180, 1198, 1204, 1240, 1249):
        weather_code = 'ασθενής βροχή'
    elif code in (1168, 1183, 1186, 1189, 1201, 1207, 1243, 1252):
        weather_code = 'βροχή'
    elif code in (1171, 1192, 1195, 1246):
        weather_code = 'έντονη βροχόπτωση'
    elif code in (1066, 1072, 1114, 1210, 1213, 1216, 1219, 1255, 1258, 1261, 1264):
        weather_code = 'χιόνι'
    elif code in (1222, 1225, 1237):
        weather_code = 'έντονη χιονόπτωση'
    elif code in (1087, 1273, 1276, 1279):
        weather_code = 'καταιγίδα'
    elif code in (1117, 1282):
        weather_code = 'καταιγίδα με χαλάζι'

    return weather_code


# weather, weekdays = get_weather(
#     open_meteo="https://api.open-meteo.com/v1/forecast?latitude=35.24&longitude=25.21&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Europe/Athens")


class ActionGetWeather(Action):
    """Responds to user with weather statistics."""

    def name(self) -> Text:
        return "action_get_weather"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # slot_value_day = tracker.get_slot('day')
        # print("slot_value_day: ", slot_value_day)
        # slot_value_hour = tracker.get_slot('hour')

        # response_test = requests.get("https://www.google.com")
        # print("response_test: ", response_test)
        # logging.info(response_test)

        weather, weekdays = get_weather(
            open_meteo="https://api.weatherapi.com/v1/forecast.json?key=09b093ac78ac4fa88ff210153233103&q=35.230000%2C25.210000&days=7&aqi=no&alerts=no&fbclid=IwAR3c1kyhw0osIyT2tY6Wzkfmd1hGiWKt7chehj75pGNhhgUtKVlWDlIwy90")

        # print("\nweekdays: ", weekdays)

        entity_day = next(tracker.get_latest_entity_values("time"), None)
        # print("entity_day1: ", entity_day)
        entity_day2 = next(tracker.get_latest_entity_values("day"), None)
        # print("entity_day2: ", entity_day2)

        if entity_day is not None:
            # Μετατροπή string σε datetime
            if type(entity_day) is not dict:
                entity_day = datetime.datetime.strptime(entity_day, "%Y-%m-%dT%H:%M:%S.%f%z")
                formatted_date = entity_day.strftime("%d-%m-%Y")
            else:
                entity_day = entity_day['to']
                entity_day = datetime.datetime.strptime(entity_day, "%Y-%m-%dT%H:%M:%S.%f%z")
                formatted_date = entity_day.strftime("%d-%m-%Y")
            weekday = entity_day.weekday()

            # get the current time in your local timezone
            local_tz = pytz.timezone('Europe/Athens')  # replace with your local timezone
            current_time = datetime.datetime.now(local_tz)

            # calculate the date 3 days ago from now
            post_three_days = current_time + datetime.timedelta(days=2)

            # print("entity_day: ", entity_day)

            # check if given date is later than 3 days from today
            if entity_day > post_three_days:
                dispatcher.utter_message(
                    "Η πρόβλεψη του καιρού για μεγάλα χρονικά διαστήματα μπορεί να είναι προβληματική και συχνά οδηγεί σε λιγότερο ακριβείς προβλέψεις. \n\nΡώτησε με ξανά για κάποια από τις επόμενες 3 ημέρες.")

            else:
                day = weather['forecast']['forecastday'][weekdays.index(weekday)]['date']

                dt = datetime.datetime.strptime(day, "%Y-%m-%d")
                # get the weekday string name
                weekday_name = dt.strftime("%A")

                weather_code = wmo_code(
                    weather['forecast']['forecastday'][weekdays.index(weekday)]['day']['condition']['code'])

                # dispatcher.utter_message("Την ημέρα {weekday} με ημερομηνία τάδε θα γίνει αυτό")
                dispatcher.utter_message(weekday_name + ', με ημερομηνία ' + str(
                    formatted_date) + ', η πρόβλεψη καιρού για την περιοχή της Μυρτιάς είναι *' + weather_code +
                                         '* και η θερμοκρασία θα κυμανθεί από: ' + str(
                    weather['forecast']['forecastday'][weekdays.index(weekday)]['day']['mintemp_c']) + "°C έως " + str(
                    weather['forecast']['forecastday'][weekdays.index(weekday)]['day']['maxtemp_c']) + "°C.")
                dispatcher.utter_message(
                    "Για πλήρη ενημέρωση του καιρού στην περιοχή της Μυρτιάς, όπου βρίσκεται το μουσείο «Νίκος Καζαντζάκης», μπορείς να δεις [εδώ](https://openweathermap.org/city/261741).")

        else:
            if entity_day2 is not None:
                # print("mpike!!")
                # get the current time in your local timezone
                # local_tz = pytz.timezone('Europe/Athens')  # replace with your local timezone
                # current_time = datetime.datetime.now(local_tz)
                # utc_now_weekday = current_time.weekday()

                entity_day2 = int(entity_day2)  # Metatropi se integer apo string
                # print("entity_day2: ", entity_day2)

                # if afairesi > 2:
                try:
                    entity_day2 = int(entity_day2)  # Metatropi se integer apo string
                    # print("entity_day2: ", entity_day2)
                    day = weather['forecast']['forecastday'][weekdays.index(entity_day2)]['date']

                    dt = datetime.datetime.strptime(day, "%Y-%m-%d")
                    formatted_date = dt.strftime("%d-%m-%Y")
                    # get the weekday string name
                    weekday_name = dt.strftime("%A")

                    weather_code = wmo_code(
                        weather['forecast']['forecastday'][weekdays.index(entity_day2)]['day']['condition']['code'])

                    # dispatcher.utter_message("Την ημέρα {weekday} με ημερομηνία τάδε θα γίνει αυτό")
                    dispatcher.utter_message(weekday_name + ', με ημερομηνία ' + str(
                        formatted_date) + ', η πρόβλεψη καιρού για την περιοχή της Μυρτιάς είναι *' + weather_code +
                                             '* και η θερμοκρασία θα κυμανθεί από: ' + str(
                        weather['forecast']['forecastday'][weekdays.index(entity_day2)]['day'][
                            'mintemp_c']) + "°C έως " + str(
                        weather['forecast']['forecastday'][weekdays.index(entity_day2)]['day']['maxtemp_c']) + "°C.")
                    dispatcher.utter_message(
                        "Για πλήρη ενημέρωση του καιρού στην περιοχή της Μυρτιάς, όπου βρίσκεται το μουσείο «Νίκος Καζαντζάκης», μπορείς να δεις [εδώ](https://openweathermap.org/city/261741).")

                except:
                    dispatcher.utter_message(
                        "Η πρόβλεψη του καιρού για μεγάλα χρονικά διαστήματα μπορεί να είναι προβληματική και συχνά οδηγεί σε λιγότερο ακριβείς προβλέψεις. \n\nΡώτησε με ξανά για κάποια από τις επόμενες 3 ημέρες.")

            else:
                # get the current time in your local timezone
                local_tz = pytz.timezone('Europe/Athens')  # replace with your local timezone
                current_time = datetime.datetime.now(local_tz)
                utc_now_weekday = current_time.weekday()

                # utc_now = datetime.datetime.now(datetime.timezone.utc)
                # utc_now_weekday = utc_now.weekday()
                day = weather['forecast']['forecastday'][weekdays.index(utc_now_weekday)]['date']
                dt = datetime.datetime.strptime(day, "%Y-%m-%d")
                formatted_date = dt.strftime("%d-%m-%Y")

                weather_code = wmo_code(
                    weather['forecast']['forecastday'][weekdays.index(utc_now_weekday)]['day']['condition']['code'])

                dispatcher.utter_message('Σήμερα με ημερομηνία ' + str(
                    formatted_date) + ', η πρόβλεψη καιρού για την περιοχή της Μυρτιάς είναι *' + str(
                    weather_code) +
                                         '* και η θερμοκρασία θα κυμανθεί από: ' + str(
                    weather['forecast']['forecastday'][weekdays.index(utc_now_weekday)]['day'][
                        'mintemp_c']) + "°C έως " + str(
                    weather['forecast']['forecastday'][weekdays.index(utc_now_weekday)]['day']['maxtemp_c']) + "°C.")

                dispatcher.utter_message(
                    "Δοκίμασε να με ρωτήσεις για οποιαδήποτε από τις επόμενες 3 ημέρες.")

        return []


def fix_greek_names(name):  # Διορθώνω την κατάληξη στα αντρικά ελληνικά ονόματα
    stop_names = ["Γιώργο", "Παύλο", "Νίκο", "Σπύρο", "Χρήστο", "Στέλιο", "Πάνο", "Θάνο", "Μάνο", "Στέργιο",
                  "Τίμο", "Χαρίτο", "Μήτσο", "Τάσο"]
    if "ς" in name[-1].lower():
        name = name[:-1]
        if "ο" in name[-1] and name not in stop_names:
            name = name[:-1] + "ε"
            return name
        else:
            return name
    elif "ο" in name[-1] and name not in stop_names:
        name = name[:-1] + "ε"
        return name
    else:
        return name


class ActionCreateGreetCarousels(Action):
    def name(self) -> Text:
        return "action_create_greet_carousels"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # ip_address = tracker.current_state()['sender_id']
        # print("ip_address: ", ip_address)

        # Τα keys για το json υπάρχουν στο παρακάτω link
        # https://github.com/botfront/rasa-webchat/blob/010c0539a6c57c426d090c7c8c1ca768ec6c81dc/src/components/Widget/components/Conversation/components/Messages/components/Carousel/index.js
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Μουσείο Νίκος Καζαντζάκης",
                        "subtitle": "Πιο συχνές κατηγορίες",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/Nikos_Kazantzakis.jpg",
                        "buttons": [
                            {
                                "title": "Τοποθεσία",
                                "payload": "τοποθεσία",
                                "type": "postback"
                            },
                            {
                                "title": "Ωράριο",
                                "payload": "ωράριο",
                                "type": "postback"
                            },
                            {
                                "title": "Εισιτήρια",
                                "payload": "εισιτήριο",
                                "type": "postback"
                            },
                            {
                                "title": "Πρόσβαση",
                                "payload": "πρόσβαση",
                                "type": "postback"
                            },
                            {
                                "title": "Πωλητήριο",
                                "payload": "πωλητήριο",
                                "type": "postback"
                            }
                        ]
                    },
                    {
                        "title": "Συλλογές Μουσείου",
                        "subtitle": "Θεματικές ενότητες",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/nikos-kazantzakis-museum.jpg",
                        "buttons": [
                            {
                                "title": "Βιογραφικά στοιχεία",
                                "payload": "αίθουσα βιογραφικά στοιχεία",
                                "type": "postback"
                            },
                            {
                                "title": "Η 'Οδύσεια'",
                                "payload": "το ποίημα της Οδύσσειας",
                                "type": "postback"
                            },
                            {
                                "title": "Επιστολές & Προσωρινά εκθέματα",
                                "payload": "οι φίλοι και οι επιρροές",
                                "type": "postback"
                            },
                            {
                                "title": "Πρώιμα έργα",
                                "payload": "τα πρώιμα και τα θεατρικά έργα",
                                "type": "postback"
                            },
                            {
                                "title": "Μυθιστορήματα",
                                "payload": "τα μυθιστορήματα και τα ταξιδιωτικά έργα",
                                "type": "postback"
                            }
                        ]
                    },
                    # {
                    #     "title": "TEST123",
                    #     "subtitle": "Aegean Solutions SA",
                    #     # "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/86/Nikos_Kazantzakis.jpg",
                    #     "buttons": [
                    #         {
                    #             "title": "Click here",
                    #             "url": "https://www.kazantzaki.gr/gr",
                    #             "type": "web_url"
                    #         }
                    #     ]
                    # }
                ]
            }
        }

        dispatcher.utter_message(attachment=message)

        name = tracker.get_slot("PERSON")
        if name is not None:
            name = fix_greek_names(name)
            dispatcher.utter_message(
                text=f"Γεια σου {name} 🙂! Μπορείς να επιλέξεις μία απο τις παραπάνω κατηγορίες ή να γράψεις μία δική σου ερώτηση.")
        else:
            dispatcher.utter_message(
                text="Γεια σου. Μπορείς να επιλέξεις μία απο τις παραπάνω κατηγορίες ή να γράψεις μία δική σου ερώτηση.")

        return []


class ActionSetReminder(Action):
    """Schedules a reminder, supplied with the last message's entities."""

    def name(self) -> Text:
        return "action_set_reminder"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # dispatcher.utter_message("Θα σε υπενθυμίσω 25 δευτερόλεπτα.")

        date = datetime.datetime.now() + datetime.timedelta(seconds=240)
        # entities = tracker.latest_message.get("entities")

        reminder = ReminderScheduled(
            "EXTERNAL_reminder",
            trigger_date_time=date,
            # entities=entities,
            name="my_reminder",
            kill_on_user_message=True,  # Whether a user message before the trigger time will abort the reminder
        )

        return [reminder]


class ActionReactToReminder(Action):
    """Reminds the user with his name when idle."""

    def name(self) -> Text:
        return "action_react_to_reminder"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("PERSON")

        weather, weekdays = get_weather(
            open_meteo="https://api.weatherapi.com/v1/forecast.json?key=09b093ac78ac4fa88ff210153233103&q=35.230000%2C25.210000&days=7&aqi=no&alerts=no&fbclid=IwAR3c1kyhw0osIyT2tY6Wzkfmd1hGiWKt7chehj75pGNhhgUtKVlWDlIwy90")

        weather_code = wmo_code(
            weather['forecast']['forecastday'][1]['day']['condition']['code'])

        if name is not None:
            name = fix_greek_names(name)
            text_list = [f"Μας ξέχασες {name}!",
                         f"Είσαι ακόμα εδώ {name}; Αν όχι, σε περιμένουμε στο μουσείο!",
                         f"Είμαι εδώ ακόμα {name}, έτοιμος να ακούσω περισσότερα από εσένα!",
                         f"Είμαι εδώ ακόμα {name}, έλα να συνεχίσουμε την κουβέντα μας!",
                         f"Αν υπάρχει κάτι που θέλεις να συζητήσουμε, είμαι εδώ για να σε βοηθήσω {name}!"]

            random_text = random.choice(text_list)

            dispatcher.utter_message(random_text)

        else:
            text_list = ["Μας ξέχασες!",
                         "Είσαι ακόμα εδώ; Αν όχι, σε περιμένουμε στο μουσείο!",
                         "Είμαι εδώ ακόμα, έτοιμος να ακούσω περισσότερα από εσένα!",
                         "Είμαι εδώ ακόμα, έλα να συνεχίσουμε την κουβέντα μας!",
                         "Αν υπάρχει κάτι που θέλεις να συζητήσουμε, είμαι εδώ για να σε βοηθήσω!"]

            random_text = random.choice(text_list)

            dispatcher.utter_message(random_text)

        if weather_code == 'καθαρός ουρανός':
            dispatcher.utter_message('Αύριο στη Μυρτιά, θα είναι μία ηλιόλουστη μέρα ☀️,'
                                     ' κατάλληλη για να μας επισκεφθείτε!')
        elif weather_code == 'βροχή' or weather_code == 'έντονη βροχόπτωση' or weather_code == 'καταιγίδα':
            dispatcher.utter_message('Αν έχεις σκοπό να μας επισκεφθείς αύριο, '
                                     'μην ξεχάσεις να κρατάς ομπρέλα ☂ μαζί σου γιατί υπάρχει πιθανότητα βροχής!')

        return []


class ActionGoodbye(Action):
    """Goodbyes the user with his name."""

    def name(self) -> Text:
        return "action_goodbye"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("PERSON")

        weather, weekdays = get_weather(
            open_meteo="https://api.weatherapi.com/v1/forecast.json?key=09b093ac78ac4fa88ff210153233103&q=35.230000%2C25.210000&days=7&aqi=no&alerts=no&fbclid=IwAR3c1kyhw0osIyT2tY6Wzkfmd1hGiWKt7chehj75pGNhhgUtKVlWDlIwy90")

        weather_code = wmo_code(
            weather['forecast']['forecastday'][1]['day']['condition']['code'])

        if name is not None:
            name = fix_greek_names(name)
            text_list = [f"Αντίο {name}, σε ευχαριστούμε για την επίσκεψη. 🙂",
                         f"Αντίο {name}, θα σε περιμένουμε στο Μουσείο. 🙂"]

            random_text = random.choice(text_list)

            dispatcher.utter_message(random_text)

            # dispatcher.utter_message(f"Αντίο {name}, σε ευχαριστούμε για την επίσκεψη.")
        else:
            text_list = ["Αντίο, σε ευχαριστούμε για την επίσκεψη. 🙂",
                         "Αντίο, θα σε περιμένουμε στο Μουσείο. 🙂",
                         "Παρακαλώ, είμαστε πάντα στην διάθεση σας. 🙂"]

            random_text = random.choice(text_list)

            dispatcher.utter_message(random_text)
            # dispatcher.utter_message("Αντίο, σε ευχαριστούμε για την επίσκεψη.")

        if weather_code == 'καθαρός ουρανός':
            dispatcher.utter_message('Αύριο στη Μυρτιά, θα είναι μία ηλιόλουστη μέρα ☀️,'
                                     ' κατάλληλη για να έρθετε από κοντά!')
        elif weather_code == 'βροχή' or weather_code == 'έντονη βροχόπτωση' or weather_code == 'καταιγίδα':
            dispatcher.utter_message('Αν έχεις σκοπό να μας επισκεφθείς αύριο, '
                                     'μην ξεχάσεις να κρατάς ομπρέλα ☂ μαζί σου γιατί υπάρχει πιθανότητα βροχής!')

        return []


# Ο λόγος που επιλέχτηκε το Carousel είναι γιατί σε κανονικά buttons ΔΕΝ μπορεί το rasa να βάλει URL μέσα
class ActionCreateSocialMediaButtons(Action):
    def name(self) -> Text:
        return "action_create_socialmedia_buttons"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Μπορείς να κάνεις Follow το Μουσείο στα παρακάτω Μέσα Κοινωνικής Δικτύωσης.")

        # Τα keys για το json υπάρχουν στο παρακάτω link
        # https://github.com/botfront/rasa-webchat/blob/010c0539a6c57c426d090c7c8c1ca768ec6c81dc/src/components/Widget/components/Conversation/components/Messages/components/Carousel/index.js
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/fb-1.jpg",
                        "buttons": [
                            {
                                "type": "web_url",
                                "title": "Facebook",
                                "url": "https://www.facebook.com/kazantzakis.museum"
                            }
                        ]
                    },
                    {
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/youtube.png",
                        "buttons": [
                            {
                                "type": "web_url",
                                "title": "Youtube",
                                "url": "https://www.youtube.com/user/kazantzakismuseum"
                            }
                        ]
                    },
                    {
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/instagram.webp",
                        "buttons": [
                            {
                                "type": "web_url",
                                "title": "Instagram",
                                "url": "https://www.instagram.com/kazantzakismuseum"
                            }
                        ]
                    },
                    {
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/trip.png",
                        "buttons": [
                            {
                                "type": "web_url",
                                "title": "Tripadvisor",
                                "url": "https://www.tripadvisor.com.gr/Attraction_Review-g8472695-d2663825-Reviews-Kazantzakis_Museum-Myrtia_Crete.html"
                            }
                        ]
                    }
                ]
            }
        }

        dispatcher.utter_message(attachment=message)

        return []


# class ActionCreateCollectionsCarousels(Action):
#     def name(self) -> Text:
#         return "action_create_collections_carousels"
#
#     def run(
#             self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         dispatcher.utter_message(
#             text="Στην κατοχή και κυριότητα του Μουσείου βρίσκεται το Αρχείο Καζαντζάκη, το οποίο περιλαμβάνει περισσότερα από 50.000 αντικείμενα, κατόπιν πολύχρονων προσπαθειών του ιδρυτή του Γιώργου Ανεμογιάννη! "
#                  "Πολλά από τα αντικείμενα εκτίθενται σε 5 θεματικές συλλογές στις 4 αίθουσες του μουσείου. Για να μάθετε περισσότερα για τα εκθέματα των συλλογών του μουσείου πατήστε εδώ. ")
#
#         # Τα keys για το json υπάρχουν στο παρακάτω link
#         # https://github.com/botfront/rasa-webchat/blob/010c0539a6c57c426d090c7c8c1ca768ec6c81dc/src/components/Widget/components/Conversation/components/Messages/components/Carousel/index.js
#         message = {
#             "type": "template",
#             "payload": {
#                 "template_type": "generic",
#                 "elements": [
#                     {
#                         "title": "Βιογραφικά στοιχεία",
#                         "subtitle": "Παιδικά χρόνια, Σύζυγοι, Φίλοι, Προσωπικά αντικείμενα",
#                         "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/βιογραφικά-στοιχεία.jpg",
#                         "buttons": [
#                             {
#                                 "title": "Βιογραφικά στοιχεία",
#                                 "payload": "αίθουσα βιογραφικά στοιχεία",
#                                 "type": "postback"
#                             }
#                         ]
#                     },
#                     {
#                         "title": "Η 'Οδύσεια'",
#                         "subtitle": "Μεγαλόπνοο έπος του Καζαντζάκη",
#                         "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/οδύσσεια.jpg",
#                         "buttons": [
#                             {
#                                 "title": "Η 'Οδύσεια'",
#                                 "payload": "το ποίημα της Οδύσσειας",
#                                 "type": "postback"
#                             }
#                         ]
#                     },
#                     {
#                         "title": "Επιρροές",
#                         "subtitle": "Επιστολές & Προσωρινά εκθέματα ",
#                         "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/φιλοι-κ-επιρροες-1024x681-1.jpg",
#                         "buttons": [
#                             {
#                                 "title": "Επιρροές, Επιστολές & Προσωρινά εκθέματα",
#                                 "payload": "οι φίλοι και οι επιρροές",
#                                 "type": "postback"
#                             }
#                         ]
#                     },
#                     {
#                         "title": "Πρώιμα έργα",
#                         "subtitle": "Θεατρικά, Παιδικά βιβλία και η 'Ασκητική'",
#                         "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/πρώιμα-θεατρικά-εργα.jpg",
#                         "buttons": [
#                             {
#                                 "title": "Πρώιμα έργα",
#                                 "payload": "τα πρώιμα και τα θεατρικά έργα",
#                                 "type": "postback"
#                             }
#                         ]
#                     },
#                     {
#                         "title": "Μυθιστορήματα",
#                         "subtitle": "'Ταξιδεύοντας...', Αναγνωστήριο, Σινεμά, Πολιτική και μελέτες για τον Καζαντζάκη",
#                         "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/μυθιστορηματα-1024x511-1.jpg",
#                         "buttons": [
#                             {
#                                 "title": "Μυθιστορήματα",
#                                 "payload": "τα μυθιστορήματα και τα ταξιδιωτικά έργα",
#                                 "type": "postback"
#                             }
#                         ]
#                     }
#                 ]
#             }
#         }
#
#         dispatcher.utter_message(attachment=message)
#
#         return []


class ActionCreateDenyCarousels(Action):
    def name(self) -> Text:
        return "action_create_deny_carousels"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Μουσείο Νίκος Καζαντζάκης",
                        "subtitle": "Πιο συχνές κατηγορίες",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/Nikos_Kazantzakis.jpg",
                        "buttons": [
                            {
                                "title": "Τοποθεσία",
                                "payload": "τοποθεσία",
                                "type": "postback"
                            },
                            {
                                "title": "Ωράριο",
                                "payload": "ωράριο",
                                "type": "postback"
                            },
                            {
                                "title": "Εισιτήρια",
                                "payload": "εισιτήριο",
                                "type": "postback"
                            },
                            {
                                "title": "Πρόσβαση",
                                "payload": "πρόσβαση",
                                "type": "postback"
                            },
                            {
                                "title": "Πωλητήριο",
                                "payload": "πωλητήριο",
                                "type": "postback"
                            }
                        ]
                    },
                    {
                        "title": "Συλλογές Μουσείου",
                        "subtitle": "Θεματικές ενότητες",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/nikos-kazantzakis-museum.jpg",
                        "buttons": [
                            {
                                "title": "Βιογραφικά στοιχεία",
                                "payload": "αίθουσα βιογραφικά στοιχεία",
                                "type": "postback"
                            },
                            {
                                "title": "Η 'Οδύσεια'",
                                "payload": "το ποίημα της Οδύσσειας",
                                "type": "postback"
                            },
                            {
                                "title": "Επιστολές & Προσωρινά εκθέματα",
                                "payload": "οι φίλοι και οι επιρροές",
                                "type": "postback"
                            },
                            {
                                "title": "Πρώιμα έργα",
                                "payload": "τα πρώιμα και τα θεατρικά έργα",
                                "type": "postback"
                            },
                            {
                                "title": "Μυθιστορήματα",
                                "payload": "τα μυθιστορήματα και τα ταξιδιωτικά έργα",
                                "type": "postback"
                            }
                        ]
                    },
                    # {
                    #     "title": "TEST123",
                    #     "subtitle": "Aegean Solutions SA",
                    #     # "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/86/Nikos_Kazantzakis.jpg",
                    #     "buttons": [
                    #         {
                    #             "title": "Click here",
                    #             "url": "https://www.kazantzaki.gr/gr",
                    #             "type": "web_url"
                    #         }
                    #     ]
                    # }
                ]
            }
        }

        dispatcher.utter_message(attachment=message)

        dispatcher.utter_message(text="Ωραία, μπορείτε να με ρωτήσετε κάτι από τα παραπάνω θέματα ή να μου κάνετε "
                                      "μια δική σας ερώτηση σχετικά με το Μουσείο «Νίκος Καζαντζάκης»! 😃")

        return []


class ActionGetConfidence(Action):
    def name(self) -> Text:
        return "action_get_confidence"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Παίρνω ΟΛΑ τα μηνύματα του χρηστή
        user_events = [event for event in tracker.events if event.get("event") == "user"]

        # Το προτελευταίο μήνυμα του χρήστη. Άμα ζητούσαμε μόνο το τελευταίο tracker.latest_message[]
        penultimate_index = len(user_events) - 2

        confidence_level_percentage = None

        for index, event in enumerate(user_events):
            if index == penultimate_index:
                if event['parse_data']['intent'] is not 'EXTERNAL_reminder':
                    confidence_level_percentage = event['parse_data']['intent']['confidence']
                    break
                else:
                    dispatcher.utter_message(
                        text='Με βάση τα δεδομένα και τις γνώσεις μου, έχω υψηλή βεβαιότητα για την ακρίβεια της απάντησής μου!')
                    return []

        confidence_level_percentage = confidence_level_percentage * 100

        if confidence_level_percentage >= 90.0:
            # confidence_level_percentage = round(confidence_level_percentage, 2)

            high_confidence_texts = [
                "Με βάση τα δεδομένα και τις γνώσεις μου, έχω υψηλή βεβαιότητα για την ακρίβεια της απάντησής μου!",
                "Βεβαιώνω με ασφάλεια, ότι η τελευταία μου απάντηση είναι σωστή!",
                "Οι πληροφορίες μου με οδηγούν στο συμπέρασμα ότι η απάντηση που έδωσα είναι σωστή!"]

            high_confidence_text = random.choice(high_confidence_texts)
            dispatcher.utter_message(text=high_confidence_text)

        elif confidence_level_percentage is None:

            high_confidence_texts = [
                "Με βάση τα δεδομένα και τις γνώσεις μου, έχω υψηλή βεβαιότητα για την ακρίβεια της απάντησής μου!",
                "Βεβαιώνω με ασφάλεια, ότι η τελευταία μου απάντηση είναι σωστή!",
                "Οι πληροφορίες μου με οδηγούν στο συμπέρασμα ότι η απάντηση που έδωσα είναι σωστή!"]

            high_confidence_text = random.choice(high_confidence_texts)
            dispatcher.utter_message(text=high_confidence_text)

        elif 70.0 < confidence_level_percentage < 90.0:
            # confidence_level_percentage = round(confidence_level_percentage, 2)

            low_confidence_texts = [
                "Με βάση τα δεδομένα και τις γνώσεις μου, είμαι σχεδόν σίγουρος για την ακρίβεια της απάντησης μου.",
                "Οι πληροφορίες μου με οδηγούν στο συμπέρασμα ότι η απάντηση που έδωσα είναι ενδεχομένως σωστή.",
                "Βεβαιώνω με κάθε επιφύλαξη, ότι η τελευταία μου απάντηση είναι σωστή."]
            # "Υπάρχει μια πιθανότητα να μην είμαι απόλυτα σίγουρος για την απάντησή μου, με ποσοστό εμπιστοσύνης {:.2f}%. Προσπάθησε να αναδιατυπώσεις την ερώτηση σου.".format(confidence_level_percentage),
            # "Μπορεί να είναι σωστή η απάντησή μου, αλλά δεν μπορώ να το εγγυηθώ με απόλυτη βεβαιότητα με συγκεκριμένο ποσοστό εμπιστοσύνης {:.2f}%. Προσπάθησε να αναδιατυπώσεις την ερώτηση σου.".format(confidence_level_percentage),
            # "Πιθανώς η απάντησή μου είναι σωστή, αλλά θα πρέπει να ληφθεί υπόψη και το ποσοστό εμπιστοσύνης {:.2f}%. Δοκίμασε να αναδιατυπώσεις την ερώτηση σου.".format(confidence_level_percentage)]

            low_confidence_text = random.choice(low_confidence_texts)
            dispatcher.utter_message(text=low_confidence_text)

        else:

            dispatcher.utter_message(
                text="Δυστυχώς, η ασφάλεια της απάντησής μου είναι πολύ χαμηλή. Ενδέχεται να μην έχω κατανοήσει καλά την ερώτησή σου ή να μην διαθέτω αρκετές πληροφορίες. Θα μπορούσατε να επαναλάβετε με άλλα λόγια;")

        return []

class ActionInitialCarousels(Action):
    def name(self) -> Text:
        return "action_initial_carousels"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Μουσείο Νίκος Καζαντζάκης",
                        "subtitle": "Πιο συχνές κατηγορίες",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/Nikos_Kazantzakis.jpg",
                        "buttons": [
                            {
                                "title": "Τοποθεσία",
                                "payload": "τοποθεσία",
                                "type": "postback"
                            },
                            {
                                "title": "Ωράριο",
                                "payload": "ωράριο",
                                "type": "postback"
                            },
                            {
                                "title": "Εισιτήρια",
                                "payload": "εισιτήριο",
                                "type": "postback"
                            },
                            {
                                "title": "Πρόσβαση",
                                "payload": "πρόσβαση",
                                "type": "postback"
                            },
                            {
                                "title": "Πωλητήριο",
                                "payload": "πωλητήριο",
                                "type": "postback"
                            }
                        ]
                    },
                    {
                        "title": "Συλλογές Μουσείου",
                        "subtitle": "Θεματικές ενότητες",
                        "image_url": "https://www.memobot.eu/wp-content/uploads/2022/10/nikos-kazantzakis-museum.jpg",
                        "buttons": [
                            {
                                "title": "Βιογραφικά στοιχεία",
                                "payload": "αίθουσα βιογραφικά στοιχεία",
                                "type": "postback"
                            },
                            {
                                "title": "Η 'Οδύσεια'",
                                "payload": "το ποίημα της Οδύσσειας",
                                "type": "postback"
                            },
                            {
                                "title": "Επιστολές & Προσωρινά εκθέματα",
                                "payload": "οι φίλοι και οι επιρροές",
                                "type": "postback"
                            },
                            {
                                "title": "Πρώιμα έργα",
                                "payload": "τα πρώιμα και τα θεατρικά έργα",
                                "type": "postback"
                            },
                            {
                                "title": "Μυθιστορήματα",
                                "payload": "τα μυθιστορήματα και τα ταξιδιωτικά έργα",
                                "type": "postback"
                            }
                        ]
                    }
                ]
            }
        }

        dispatcher.utter_message(attachment=message)

        return []

class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_query = tracker.latest_message.get("text")
        print(user_query)
        # Call your RAG model API
        
        response = utils.action_openai_chat_completion(
            dispatcher,
            system_prompt=genai_data["tasks"]["fallback_prompts"]["system_prompt"],
            user_prompt=genai_data["tasks"]["fallback_prompts"]["user_prompt"].format(
                query=user_query),
            chat_model=CHAT_MODEL,
            endpoint_url=f"{GENAI_BASE_URL}/{OPENAI_RESPONSE_ENDPOINT}"
        )

        # Send the response back to the user
        dispatcher.utter_message(text=response)

        return []
