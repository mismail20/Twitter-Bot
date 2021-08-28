from __future__ import print_function
import tweepy

# --------------- Connecting Twitter Account ----------------------

CONSUMER_KEY = 'YOUR CODE'
CONSUMER_SECRET = 'YOUR CODE'
ACCESS_KEY = 'YOUR CODE'
ACCESS_SECRET = 'YOUR CODE'

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


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


# --------------- Promotional tweet function ------------------

# Function that posts promotional tweets. It picks between 3 messages, it checks if the messages has been sent within the past two tweets, if not then it will post it. This is to avoid duplicate tweets.

def send_tweet():

    message_1 = 'Need a Logo? GFX? Revamp? feel free to drop us a DM! \n Port: neosdesigns.portfoliobox.net \n \n @SGH_RTs @TwitchReTweets @CAE_RT @BlazedRTs @SmallStreamers @SupStreamersRT @DripRT @ScrimFinder @GamerGalsRT -'
    message_2 = 'Do you need a Graphics Designer? \n Port: neosdesigns.portfoliobox.net \n \n @SGH_RTs @TwitchReTweets @CAE_RT @BlazedRTs @SmallStreamers @SupStreamersRT @DripRT @ScrimFinder @GamerGalsRT +'
    message_3 = 'Get your Twitch Graphics here! \n Port: neosdesigns.portfoliobox.net \n \n @SGH_RTs @TwitchReTweets @CAE_RT @BlazedRTs @SmallStreamers @SupStreamersRT @DripRT @ScrimFinder @GamerGalsRT ~'

    messages = [message_1,message_2,message_3]

    tweet_list = api.user_timeline(count=2, tweet_mode="extended")
    latest_tweet = tweet_list[0].full_text
    previous_tweet = tweet_list[1].full_text


    for message in messages:
        if message[-1] == latest_tweet[-1] or message[-1] == previous_tweet[-1]:
            print("Selecting another tweet")
        else:
            api.update_status(message)
            break
        
# --------------- Functions that state what happens when you start or end the skill  ----------------------          
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Would you like to send a custom tweet, or some promotional tweets?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Sorry, I dont think you heard me, Would you like to send a custom tweet, or some promotional tweets?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Mohamed's Twitter Bot. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
        
 # --------------- Functions that give responses based on intent  ----------------------   
def get_promotional_response():
    session_attributes = {}
    card_title = "Promotional"
    send_tweet()
    speech_output = "Promotional Tweet Sent"
    should_end_session = True
    reprompt_text = "You never responded to the first test message. Sending another one."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_custom_response():
    session_attributes = {}
    card_title = "Custom"
    speech_output = "Say, Twitter Bot post, Followed by your Custom Tweet"
    should_end_session = False
    reprompt_text = "Sorry I dont think you heard me, Say, Twitter Bot Post, Followed by your Custom Tweet"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Stores User input and posts it to twitter through api ----------------------
def get_custom_tweet(intent):
    session_attributes = {}
    card_title = "Custom"
    custom_tweet = intent['slots']['tweet']['value']
    speech_output =  f'Sending, {custom_tweet} , to Twitter'
    api.update_status(custom_tweet)
    should_end_session = True
    reprompt_text = "Sorry I dont think you heard me, Say, My Custom Tweet is, Followed by your Custom Tweet"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



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
    if intent_name == "promotional":
        return get_promotional_response()
    elif intent_name == "custom":
        return get_custom_response()
    elif intent_name == "getCustomTweet":
        return get_custom_tweet(intent)
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
    print("Incoming request...")

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