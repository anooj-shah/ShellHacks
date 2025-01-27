"""
This is the compliment application for part 1 of my alexa series. 
Make sure to add compliments.txt (found on the github page) to the same directory as this file
in AWS lambda in order for this to work.
"""

from __future__ import print_function
import random
import requests

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
def get_student_question(intent, session):
    print("SESSION INTENT", session, intent)
    # print("ATTRIBUTES:", session.attributes)
    session_attributes = {}
    card_title = "Question"
    # questions = ["How do you reverse a linked list", "How do I become the tech lead", "What is 2 plus 2"]
    payload = {'sessionId': "123321"}
    questions = requests.get('https://doublecheckapp.herokuapp.com/question', params=payload).json()
    print("QUESTIONS", questions)
    # TODO: 'question' should get the one with the most upvotes
    question = questions[0]
    question = question['questionBody']
    print(question)
    # question = questions[random.randint(0, len(questions)-1)]
    speech_output = question
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_quiz_response():
    session_attributes = {}
    card_title = "Question"
    questions = ["How do you reverse a linked list", "How do I become the tech lead", "What is 2 plus 2"]
    question = questions[random.randint(0, len(questions)-1)]
    speech_output = question
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_compliment_response():
    """ Have alexa give you a random compliment out of a list of 100. 
        Make sure to add the compliments.txt file to same directory as this one
        in order for this to work.
    """
    session_attributes = {}
    card_title = "Compliment"
    compliments = [line for line in open('compliments.txt')]
    print(compliments)
    compliment = compliments[random.randint(0,len(compliments)-1)]
    speech_output = compliment
    reprompt_text = "I said," + compliment
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
    """ Message that is sent right when you launch your application
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "What up what up what up, your application has started!"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, welcome to your custom alexa application!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific 
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass

    

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "compliment":
        return get_compliment_response()
    elif intent_name == "question":
        return get_student_question(intent, session)
    elif intent_name == "quiz":
        return get_quiz_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...", event, context)

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])