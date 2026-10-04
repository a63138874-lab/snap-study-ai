import time
import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Snap & Study AI",
    page_icon="📚",
)


# ---------------------------------------------------------
# GEMINI CLIENT
# ---------------------------------------------------------

@st.cache_resource
def get_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_client()


# ---------------------------------------------------------
# EMAIL FUNCTION
# ---------------------------------------------------------

def send_summary_email(recipient_email, summary):

    sender_email = st.secrets["GMAIL_SENDER_EMAIL"]
    app_password = st.secrets["GMAIL_APP_PASSWORD"]

    message = MIMEText(
        summary,
        "plain",
        "utf-8"
    )

    message["Subject"] = (
        "📚 Your Snap & Study AI Revision Summary"
    )

    message["From"] = sender_email
    message["To"] = recipient_email

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            sender_email,
            app_password
        )

        server.send_message(message)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "started" not in st.session_state:
    st.session_state.started = False

if "name" not in st.session_state:
    st.session_state.name = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "chat" not in st.session_state:
    st.session_state.chat = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""


# ---------------------------------------------------------
# APP HEADER
# ---------------------------------------------------------

st.title("📚 Snap & Study AI")

st.markdown(
    "### Learn smarter. Understand faster. 🚀"
)

st.caption(
    "Ask questions, upload notes or diagrams, solve problems, "
    "and create quick revision summaries with AI."
)


# ---------------------------------------------------------
# ONBOARDING
# ---------------------------------------------------------

if not st.session_state.started:

    st.subheader("Welcome! 👋")

    name = st.text_input(
        "Enter your name"
    )

    email = st.text_input(
        "Enter your email"
    )

    if st.button(
        "Start Studying 🚀",
        type="primary"
    ):

        if not name.strip():

            st.warning(
                "Please enter your name."
            )

            st.stop()

        if not email.strip():

            st.warning(
                "Please enter your email."
            )

            st.stop()

        st.session_state.name = name.strip()
        st.session_state.email = email.strip()

        st.session_state.chat = client.chats.create(
            model="gemini-3.8-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
        )

        welcome = WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": welcome,
            }
        )

        st.session_state.started = True

        st.rerun()


# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------

else:

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    with st.sidebar:

        st.header("👤 Student")

        st.write(
            f"**Name:** {st.session_state.name}"
        )

        st.write(
            f"**Email:** {st.session_state.email}"
        )

        st.divider()

        if st.button(
            "🗑️ Clear Chat"
        ):

            st.session_state.messages = []

            st.session_state.summary = ""

            st.session_state.chat = client.chats.create(
                model="gemini-3.8-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.rerun()


    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    prompt = st.chat_input(
        "Ask a question or upload an image...",
        accept_file=True,
        file_type=[
            "jpg",
            "jpeg",
            "png"
        ],
    )


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    if prompt:

        user_text = prompt.text.strip()

        files = prompt.files


        if not user_text and not files:

            st.warning(
                "Please type a question or upload an image."
            )

            st.stop()


        # Display user message

        with st.chat_message("user"):

            if user_text:

                st.markdown(
                    user_text
                )

            if files:

                st.image(
                    files[0]
                )


        # Prepare Gemini content

        contents = []


        if user_text:

            contents.append(
                user_text
            )


        if files:

            image = files[0]

            image_part = types.Part.from_bytes(
                data=image.getvalue(),
                mime_type=image.type,
            )

            contents.append(
                image_part
            )


        # Save user message

        st.session_state.messages.append(
            {
                "role": "user",
                "content": (
                    user_text
                    if user_text
                    else "📷 Uploaded an image"
                ),
            }
        )


        # -------------------------------------------------
        # GEMINI RESPONSE
        # -------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking... 🤔"
            ):

                try:

                    response = None


                    # Retry temporary 503 errors

                    for attempt in range(3):

                        try:

                            response = (
                                st.session_state.chat.send_message(
                                    contents
                                )
                            )

                            break


                        except Exception as e:

                            error_message = str(e)


                            if (
                                "503" in error_message
                                or "UNAVAILABLE" in error_message
                            ):

                                if attempt < 2:

                                    time.sleep(3)

                                else:

                                    raise


                            else:

                                raise


                    answer = response.text

                    st.markdown(
                        answer
                    )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )


                except Exception as e:

                    error_message = str(e)


                    if (
                        "503" in error_message
                        or "UNAVAILABLE" in error_message
                    ):

                        st.warning(
                            "🤖 Gemini AI is temporarily busy "
                            "right now. Please wait a little "
                            "and try again."
                        )


                    elif (
                        "429" in error_message
                        or "RESOURCE_EXHAUSTED" in error_message
                    ):

                        st.warning(
                            "⏳ Gemini usage limit has been "
                            "reached for now. Please try "
                            "again after the quota resets."
                        )


                    elif (
                        "401" in error_message
                        or "403" in error_message
                    ):

                        st.error(
                            "🔐 There is an API authentication "
                            "problem. Please check the Gemini "
                            "API configuration."
                        )


                    else:

                       st.error(
                               "⚠️ Something went wrong while getting the AI response."
                        )

                       st.code(error_message)


    # -----------------------------------------------------
    # SUMMARY SECTION
    # -----------------------------------------------------

    st.divider()


    if st.button(
        "📋 Generate Study Summary"
    ):

        if len(st.session_state.messages) < 2:

            st.info(
                "Start a conversation first."
            )


        else:

            with st.spinner(
                "Creating your study summary... 🧠"
            ):

                try:

                    response = None


                    # Retry temporary 503 errors

                    for attempt in range(5):

                        try:

                            response = (
                                st.session_state.chat.send_message(
                                    SUMMARY_REQUEST_PROMPT
                                )
                            )

                            break


                        except Exception as e:

                            error_message = str(e)


                            if (
                                "503" in error_message
                                or "UNAVAILABLE" in error_message
                            ):

                                if attempt < 4:

                                    wait_time = 3 * (
                                        attempt + 1
                                    )

                                    time.sleep(
                                        wait_time
                                    )

                                else:

                                    raise


                            else:

                                raise


                    summary_text = response.text


                    if summary_text:

                        st.session_state.summary = (
                            summary_text
                        )

                        st.subheader(
                            "📋 Study Summary"
                        )

                        st.markdown(
                            summary_text
                        )


                except Exception as e:

                    error_message = str(e)


                    if (
                        "503" in error_message
                        or "UNAVAILABLE" in error_message
                    ):

                        st.warning(
                            "🤖 Gemini AI is temporarily busy. "
                            "Your summary could not be generated "
                            "right now. Please try again later."
                        )


                    elif (
                        "429" in error_message
                        or "RESOURCE_EXHAUSTED" in error_message
                    ):

                        st.warning(
                            "⏳ Gemini usage limit has been "
                            "reached. Please wait until the "
                            "quota resets before generating "
                            "the summary again."
                        )


                    elif (
                        "401" in error_message
                        or "403" in error_message
                    ):

                        st.error(
                            "🔐 Gemini API authentication failed. "
                            "Please check your API configuration."
                        )


                    else:

                        st.error(
                            "⚠️ We couldn't generate your "
                            "study summary right now. "
                            "Please try again later."
                        )


    # -----------------------------------------------------
    # EMAIL SUMMARY SECTION
    # -----------------------------------------------------

    if st.session_state.summary:

        st.divider()

        st.subheader(
            "📧 Email Your Revision Summary"
        )

        st.write(
            "Your study summary is ready. "
            "You can send it to your registered email."
        )


        if st.button(
            "📧 Send Summary to Email",
            type="primary"
        ):

            with st.spinner(
                "Sending your summary... 📤"
            ):

                try:

                    send_summary_email(
                        st.session_state.email,
                        st.session_state.summary
                    )


                    st.success(
                        f"📬 Summary sent successfully "
                        f"to {st.session_state.email}!"
                    )


                except Exception as e:

                    error_message = str(e)


                    if (
                        "535" in error_message
                        or "authentication"
                        in error_message.lower()
                    ):

                        st.error(
                            "🔐 Gmail authentication failed. "
                            "Please check your Gmail App Password."
                        )


                    elif "SMTP" in error_message:

                        st.error(
                            "📧 Email service is temporarily "
                            "unavailable. Please try again later."
                        )


                    else:

                        st.error(
                            "⚠️ We couldn't send the email "
                            "right now. Please try again later."
                        )