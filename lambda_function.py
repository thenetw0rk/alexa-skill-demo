import urllib2
import json

API_BASE="http://bartjsonapi.elasticbeanstalk.com/api"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.echo-sdk-ams.app.bd304b90-xxxx-xxxx-xxxx-xxxxd4772bab"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetStatus":
        return get_system_status()
    elif intent_name == "GetTemp":
        return get_temp_status()
    elif intent_name == "GetComputer":
        return get_computer_status()
    elif intent_name == "GetRoom":
        return get_room_list(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Hindley Household - Thanks"
    speech_output = "Thank you for using the Hindley Skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Hindley"
    speech_output = "Welcome to the Hindley Family Status Skill. " \
                    "You can ask me for status from any room, or " \
                    "ask me for system status or who's connected to the internet."
    reprompt_text = "Please ask me for a current status from a room, " \
                    "for example Livingoom."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_system_status():
    session_attributes = {}
    card_title = "Hindley System Status"
    reprompt_text = ""
    should_end_session = False

    response = urllib2.urlopen(API_BASE + "/status")
    bart_system_status = json.load(response)   
temperature
    speech_output = "There are currently " + bart_system_status["devicecount"] + " connected. "

    if len(bart_system_status["message"]) > 0:
        speech_output += bart_system_status["message"]
    else:
        speech_output += "Everything is running normally."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_temp_status():
    session_attributes = {}
    card_title = "Temperature Status"
    reprompt_text = ""
    should_end_session = False

    response = urllib2.urlopen(API_BASE + "/tempstatus")
    bart_temp_status = json.load(response) 

    speech_output = "Temp status. " + bart_temp_status["bsa"]["description"]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_room_list(intent):
    session_attributes = {}
    card_title = "Room List"
    speech_output = "I'm not sure which room you wanted status for. " \
                    "Please try again."
    reprompt_text = "I'm not sure which room you wanted status for. " \
                    "Try asking about Livingroom or Kitchen for example."
    should_end_session = False

    if "Room" in intent["slots"]:
        room_name = intent["slots"]["Room"]["value"]
        room_code = get_room_code(room_name.lower())

        if (room_code != "unkn"):
            card_title = "Status from " + station_name.title()

            response = urllib2.urlopen(API_BASE + "/room/" + room_code)
            room_status = json.load(response)   

            speech_output = "Status from  " + station_name + " are as follows: "
            for device in room_status["etd"]:
                speech_output += "Temp for " + device["device"] + " is " + device["devicetemp"] + ". ";
                reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_room_list(room_name):
    return {
        "LivingRoom": "lr",
        "Kitchen": "kit",
        "Hallway": "hw",
        "Stairs": "st",
        "Alfies": "al",
        "Babys": "ba",
        "Master": "ma",
        "Girls": "gi",
        "Bathroom": "br",
        "Shower": "sh",
        "Poach": "po",
        "Garage": "ga",
    }.get(room_name, "unkn")

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
