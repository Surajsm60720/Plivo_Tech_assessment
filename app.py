"""
InspireWorks IVR Demo System
Multi-level IVR with Plivo Voice API
"""

from flask import Flask, request, jsonify, send_from_directory
import plivo
from plivo import plivoxml
from config import (
    PLIVO_AUTH_ID,
    PLIVO_AUTH_TOKEN,
    PLIVO_FROM_NUMBER,
    ASSOCIATE_NUMBER,
    BASE_URL,
    AUDIO_URL_EN,
    AUDIO_URL_ES,
)

app = Flask(__name__, static_folder="static")

# Plivo client for making outbound calls
client = plivo.RestClient(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN)


# ============================================================================
# STATIC FILE SERVING
# ============================================================================


@app.route("/")
def index():
    """Serve the frontend UI"""
    return send_from_directory("static", "index.html")


# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.route("/api/make-call", methods=["POST"])
def make_call():
    """
    Initiate an outbound call to the specified phone number.
    Request body: { "phone_number": "+1234567890" }
    """
    data = request.json
    phone_number = data.get("phone_number")

    if not phone_number:
        return jsonify({"success": False, "error": "Phone number is required"}), 400

    # Ensure E.164 format
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number

    print(f"[DEBUG] Making call to: {phone_number}")
    print(f"[DEBUG] From: {PLIVO_FROM_NUMBER}")
    print(f"[DEBUG] Answer URL: {BASE_URL}/ivr/welcome")

    try:
        response = client.calls.create(
            from_=PLIVO_FROM_NUMBER,
            to_=phone_number,
            answer_url=f"{BASE_URL}/ivr/welcome",
            answer_method="POST",
        )
        print(f"[DEBUG] Call created: {response}")
        return jsonify(
            {
                "success": True,
                "message": f"Call initiated to {phone_number}",
                "call_uuid": response.request_uuid,
            }
        )
    except plivo.exceptions.PlivoRestError as e:
        print(f"[ERROR] Plivo API Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        print(f"[ERROR] Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# IVR ENDPOINTS
# ============================================================================


@app.route("/ivr/welcome", methods=["GET", "POST"])
def ivr_welcome():
    """
    Level 1: Welcome message and language selection
    Press 1 for English, Press 2 for Spanish
    """
    response = plivoxml.ResponseElement()
    
    # Check if this is a retry due to error
    # Check retry reason
    is_error = request.values.get("error") == "true"
    is_no_input = request.values.get("no_input") == "true"
    
    prompt = "Welcome to InspireWorks. Press 1 for English. Press 2 for Spanish."
    if is_error:
        prompt = "Sorry, that was an invalid selection. Press 1 for English. Press 2 for Spanish."
    elif is_no_input:
        prompt = "Sorry, I didn't hear anything. Press 1 for English. Press 2 for Spanish."

    # Get user input with language selection prompt
    get_input = plivoxml.GetInputElement(
        action=f"{BASE_URL}/ivr/language-selected",
        method="POST",
        input_type="dtmf",
        digit_end_timeout="5",
        num_digits="1",
        redirect="true",
    )

    get_input.add_speak(
        content=prompt,
        voice="Polly.Joanna",
        language="en-US",
    )

    response.add(get_input)

    # Get retry count
    retry_count = int(request.values.get("retry_count", 0))

    if retry_count < 3:
        # Retry on timeout
        redirect_url = f"{BASE_URL}/ivr/welcome?retry_count={retry_count + 1}&no_input=true"
        response.add_redirect(redirect_url)
    else:
        # Max retries reached
        response.add_speak(
            content="We did not receive any input. Goodbye.",
            voice="Polly.Joanna",
            language="en-US",
        )
        response.add_hangup()

    return response.to_string(), 200, {"Content-Type": "application/xml"}


@app.route("/ivr/language-selected", methods=["GET", "POST"])
def ivr_language_selected():
    """
    Handle Level 1 input and route to appropriate Level 2 menu
    """
    digits = request.values.get("Digits", "")
    response = plivoxml.ResponseElement()

    if digits == "1":
        # English selected - redirect to English menu
        response.add_redirect(f"{BASE_URL}/ivr/menu?lang=en")
    elif digits == "2":
        # Spanish selected - redirect to Spanish menu
        response.add_redirect(f"{BASE_URL}/ivr/menu?lang=es")
    else:
        # Invalid input - redirect back to welcome with error flag (no retry increment for invalid keys, just loop)
        response.add_redirect(f"{BASE_URL}/ivr/welcome?error=true")

    return response.to_string(), 200, {"Content-Type": "application/xml"}


@app.route("/ivr/menu", methods=["GET", "POST"])
def ivr_menu():
    """
    Level 2: Menu options based on selected language
    Press 1 to hear a message, Press 2 to speak with an associate
    """
    lang = request.values.get("lang", "en")
    is_error = request.values.get("error") == "true"
    is_no_input = request.values.get("no_input") == "true"
    retry_count = int(request.values.get("retry_count", 0))
    response = plivoxml.ResponseElement()

    # Determine prompt content based on language and error state
    if lang == "es":
        prompt = "Presione 1 para escuchar un mensaje. Presione 2 para hablar con un asociado."
        if is_error:
            prompt = "Selección inválida. " + prompt
        elif is_no_input:
            prompt = "No escuchamos nada. " + prompt
        voice = "Polly.Mia"
        language = "es-MX"
    else:
        prompt = "Press 1 to hear a message. Press 2 to speak with an associate."
        if is_error:
            prompt = "Sorry, that was an invalid selection. " + prompt
        elif is_no_input:
            prompt = "Sorry, I didn't hear anything. " + prompt
        voice = "Polly.Joanna"
        language = "en-US"

    get_input = plivoxml.GetInputElement(
        action=f"{BASE_URL}/ivr/action?lang={lang}",
        method="POST",
        input_type="dtmf",
        digit_end_timeout="5",
        num_digits="1",
        redirect="true",
    )

    get_input.add_speak(
        content=prompt,
        voice=voice,
        language=language,
    )

    response.add(get_input)

    # Fallback if no input (Timeout)
    if retry_count < 3:
        redirect_url = f"{BASE_URL}/ivr/menu?lang={lang}&retry_count={retry_count + 1}&no_input=true"
        response.add_redirect(redirect_url)
    else:
        # Max retries reached - hangup
        if lang == "es":
            response.add_speak(
                content="No recibimos ninguna entrada. Adiós.",
                voice="Polly.Mia",
                language="es-MX",
            )
        else:
            response.add_speak(
                content="We did not receive any input. Goodbye.",
                voice="Polly.Joanna",
                language="en-US",
            )
        response.add_hangup()

    return response.to_string(), 200, {"Content-Type": "application/xml"}


@app.route("/ivr/action", methods=["GET", "POST"])
def ivr_action():
    """
    Handle Level 2 input - play audio or connect to associate
    """
    digits = request.values.get("Digits", "")
    lang = request.values.get("lang", "en")
    response = plivoxml.ResponseElement()

    if digits == "1":
        # Play audio message
        if lang == "es":
            response.add_speak(
                content="Reproduciendo su mensaje ahora.",
                voice="Polly.Mia",
                language="es-MX",
            )
            response.add_play(AUDIO_URL_ES)
            response.add_speak(
                content="Gracias por llamar a InspireWorks. Adiós.",
                voice="Polly.Mia",
                language="es-MX",
            )
        else:
            response.add_speak(
                content="Playing your message now.",
                voice="Polly.Joanna",
                language="en-US",
            )
            response.add_play(AUDIO_URL_EN)
            response.add_speak(
                content="Thank you for calling InspireWorks. Goodbye.",
                voice="Polly.Joanna",
                language="en-US",
            )
        response.add_hangup()

    elif digits == "2":
        # Connect to associate
        if lang == "es":
            response.add_speak(
                content="Conectándole con un asociado. Por favor espere.",
                voice="Polly.Mia",
                language="es-MX",
            )
        else:
            response.add_speak(
                content="Connecting you to an associate. Please hold the line.",
                voice="Polly.Joanna",
                language="en-US",
            )

        # Dial the associate number
        dial = plivoxml.DialElement(
            caller_id=PLIVO_FROM_NUMBER,
            action=f"{BASE_URL}/ivr/dial-status",
            method="POST",
        )
        dial.add_number(ASSOCIATE_NUMBER)
        response.add(dial)

    else:
        # Invalid input - redirect back to menu with error flag
        response.add_redirect(f"{BASE_URL}/ivr/menu?lang={lang}&error=true")

    return response.to_string(), 200, {"Content-Type": "application/xml"}


@app.route("/ivr/dial-status", methods=["GET", "POST"])
def ivr_dial_status():
    """
    Handle dial completion status
    """
    dial_status = request.values.get("DialStatus", "")
    response = plivoxml.ResponseElement()

    if dial_status == "completed":
        response.add_speak(
            content="Thank you for calling InspireWorks. Goodbye.",
            voice="Polly.Joanna",
            language="en-US",
        )
    else:
        response.add_speak(
            content="We were unable to connect you. Please try again later. Goodbye.",
            voice="Polly.Joanna",
            language="en-US",
        )

    response.add_hangup()
    return response.to_string(), 200, {"Content-Type": "application/xml"}


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║           InspireWorks IVR Demo System                       ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Server running at: http://localhost:5001                    ║
    ║                                                              ║
    ║  IMPORTANT: Update BASE_URL in .env with your tunnel URL     ║
    ║  before making calls!                                        ║
    ║                                                              ║
    ║  Endpoints:                                                  ║
    ║    - Frontend: http://localhost:5001                         ║
    ║    - Make Call: POST /api/make-call                          ║
    ║    - IVR Webhooks: /ivr/*                                    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host="0.0.0.0", port=5001, debug=True)
