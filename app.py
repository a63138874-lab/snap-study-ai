import time
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)


st.set_page_config(
    page_title="Snap & Study AI",
    page_icon="📚",
)


@st.cache_resource
def get_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
def send_summary_email(recipient_email, summary):
    sender_email = st.secrets["GMAIL_SENDER_EMAIL"]
    app_password = st.secrets["GMAIL_APP_PASSWORD"]

    message = MIMEText(summary, "plain", "utf-8")
    message["Subject"] = "📚 Your Snap & Study AI Revision Summary"
    message["From"] = sender_email
    message["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(message)


client = get_client()


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


st.title("📚 Snap & Study AI")
st.caption("Your AI study assistant for questions, notes and images")


if not st.session_state.started:

    st.subheader("Welcome! 👋")

    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")

    if st.button("Start Studying 🚀", type="primary"):

        if not name.strip():
            st.warning("Please enter your name.")
            st.stop()

        if not email.strip():
            st.warning("Please enter your email.")
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


else:

    with st.sidebar:

        st.header("👤 Student")
        st.write(f"**Name:** {st.session_state.name}")
        st.write(f"**Email:** {st.session_state.email}")

        if st.button("🗑️ Clear Chat"):

            st.session_state.messages = []

            st.session_state.chat = client.chats.create(
                model="gemini-3.8-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.rerun()


    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    prompt = st.chat_input(
        "Ask a question or upload an image...",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],
    )


    if prompt:

        user_text = prompt.text.strip()
        files = prompt.files

        if not user_text and not files:
            st.warning("Please type a question or upload an image.")
            st.stop()


        with st.chat_message("user"):

            if user_text:
                st.markdown(user_text)

            if files:
                st.image(files[0])


        contents = []


        if user_text:
            contents.append(user_text)


        if files:

            image = files[0]

            image_part = types.Part.from_bytes(
                data=image.getvalue(),
                mime_type=image.type,
            )

            contents.append(image_part)


        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_text if user_text else "📷 Uploaded an image",
            }
        )


        with st.chat_message("assistant"):

            with st.spinner("Thinking... 🤔"):

                try:

                    response = None

                    for attempt in range(3):

                        try:

                            response = st.session_state.chat.send_message(
                                contents
                            )

                            break

                        except Exception as e:

                            if "503" in str(e) or "UNAVAILABLE" in str(e):

                                if attempt < 2:
                                    time.sleep(3)

                                else:
                                    raise e

                            else:
                                raise e


                    answer = response.text

                    st.markdown(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )


                except Exception as e:

                    st.error(f"Something went wrong: {e}")


    st.divider()


    if st.button("📋 Generate Study Summary"):

        if len(st.session_state.messages) < 2:

            st.info("Start a conversation first.")


        else:

            with st.spinner("Creating summary..."):

                try:

                    response = None

                    for attempt in range(5):

                        try:

                            response = st.session_state.chat.send_message(
                                SUMMARY_REQUEST_PROMPT
                            )

                            break


                        except Exception as e:

                            if "503" in str(e) or "UNAVAILABLE" in str(e):

                                if attempt < 4:

                                    wait_time = 3 * (attempt + 1)
                                    time.sleep(wait_time)

                                else:
                                    raise e

                            else:
                                raise e


                    st.subheader("📋 Study Summary")
                    st.markdown(response.text)

                    summary_text = response.text

                    if st.button("📧 Send Summary to Email"):

                        with st.spinner("Sending summary... 📤"):

                             try:
                                   send_summary_email(
                                             st.session_state.email,
                                             summary_text
                                )

                                   st.success(
                                            f"Summary sent successfully to {st.session_state.email} ✅"
                                )

                             except Exception as e:
                                    st.error(f"Could not send email: {e}")


                except Exception as e:

                    st.error(f"Could not generate summary: {e}")