// ============================================================
// MEDAI CHAT APPLICATION
// ============================================================

const chatBox =
    document.getElementById("chatBox");

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    const message =
        messageInput.value.trim();

    // --------------------------------------------------------
    // EMPTY MESSAGE
    // --------------------------------------------------------

    if (!message) {
        return;
    }

    // --------------------------------------------------------
    // ADD USER MESSAGE
    // --------------------------------------------------------

    addMessage(
        message,
        "user"
    );

    // --------------------------------------------------------
    // CLEAR INPUT
    // --------------------------------------------------------

    messageInput.value = "";

    // --------------------------------------------------------
    // DISABLE BUTTON
    // --------------------------------------------------------

    sendButton.disabled = true;

    // --------------------------------------------------------
    // SHOW TYPING
    // --------------------------------------------------------

    const typingId =
        showTyping();

    try {

        // ====================================================
        // SEND REQUEST TO FLASK
        // ====================================================

        const response = await fetch(
            "/api/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message: message
                })
            }
        );

        // ----------------------------------------------------
        // REMOVE TYPING
        // ----------------------------------------------------

        removeTyping(
            typingId
        );

        // ----------------------------------------------------
        // CHECK SERVER RESPONSE
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                "Server error: "
                + response.status
            );
        }

        // ----------------------------------------------------
        // READ JSON
        // ----------------------------------------------------

        const data =
            await response.json();

        console.log(
            "MedAI response:",
            data
        );

        // ----------------------------------------------------
        // GET ANSWER
        // ----------------------------------------------------

        const answer =
            data.response
            || data.answer
            || data.message;

        // ----------------------------------------------------
        // DISPLAY ANSWER
        // ----------------------------------------------------

        if (answer) {

            addMessage(
                answer,
                "bot"
            );

        } else {

            addMessage(
                "Sorry, I could not generate a response.",
                "bot"
            );
        }

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        removeTyping(
            typingId
        );

        addMessage(
            "⚠️ Unable to connect to the Medical AI server. Please make sure Flask is running.",
            "bot"
        );

    }

    // --------------------------------------------------------
    // ENABLE BUTTON
    // --------------------------------------------------------

    sendButton.disabled = false;

    messageInput.focus();
}


// ============================================================
// ADD MESSAGE
// ============================================================

function addMessage(
    text,
    sender
) {

    const message =
        document.createElement("div");

    message.className =
        "message " + sender;


    // --------------------------------------------------------
    // AVATAR
    // --------------------------------------------------------

    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar";

    avatar.textContent =
        sender === "bot"
            ? "🤖"
            : "👤";


    // --------------------------------------------------------
    // CONTENT
    // --------------------------------------------------------

    const content =
        document.createElement("div");

    content.className =
        "message-content";


    // --------------------------------------------------------
    // NAME
    // --------------------------------------------------------

    const name =
        document.createElement("div");

    name.className =
        "message-name";

    name.textContent =
        sender === "bot"
            ? "MedAI"
            : "You";


    // --------------------------------------------------------
    // BUBBLE
    // --------------------------------------------------------

    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";


    // --------------------------------------------------------
    // TEXT
    // --------------------------------------------------------

    const paragraph =
        document.createElement("p");

    paragraph.textContent =
        text;


    // --------------------------------------------------------
    // BUILD ELEMENT
    // --------------------------------------------------------

    bubble.appendChild(
        paragraph
    );

    content.appendChild(
        name
    );

    content.appendChild(
        bubble
    );

    message.appendChild(
        avatar
    );

    message.appendChild(
        content
    );

    chatBox.appendChild(
        message
    );


    // --------------------------------------------------------
    // SCROLL
    // --------------------------------------------------------

    chatBox.scrollTop =
        chatBox.scrollHeight;
}


// ============================================================
// EXAMPLE QUESTIONS
// ============================================================

function askExample(
    question
) {

    messageInput.value =
        question;

    sendMessage();
}


// ============================================================
// ENTER KEY
// ============================================================

function handleKey(
    event
) {

    if (
        event.key === "Enter"
    ) {

        event.preventDefault();

        sendMessage();
    }
}


// ============================================================
// TYPING INDICATOR
// ============================================================

function showTyping() {

    const id =
        "typing-" +
        Date.now();

    const message =
        document.createElement("div");

    message.className =
        "message bot";

    message.id =
        id;

    message.innerHTML = `

        <div class="message-avatar">
            🤖
        </div>

        <div class="message-content">

            <div class="message-name">
                MedAI
            </div>

            <div class="bubble typing-bubble">

                <span class="typing-dot"></span>

                <span class="typing-dot"></span>

                <span class="typing-dot"></span>

            </div>

        </div>
    `;

    chatBox.appendChild(
        message
    );

    chatBox.scrollTop =
        chatBox.scrollHeight;

    return id;
}


// ============================================================
// REMOVE TYPING
// ============================================================

function removeTyping(
    id
) {

    const element =
        document.getElementById(
            id
        );

    if (element) {

        element.remove();
    }
}


// ============================================================
// CLEAR CHAT
// ============================================================

function clearChat() {

    chatBox.innerHTML = `

        <div class="hero">

            <div class="hero-badge">
                <span class="pulse"></span>
                AI HEALTH ASSISTANT
            </div>

            <div class="hero-icon">
                <div class="hero-icon-inner">
                    🩺
                </div>
            </div>

            <h2>
                Your questions,
                <span>understood.</span>
            </h2>

            <p>
                Ask MedAI about common health topics,
                symptoms, prevention, and general
                medical information.
            </p>

        </div>

        <div class="message bot">

            <div class="message-avatar">
                🤖
            </div>

            <div class="message-content">

                <div class="message-header">

                    <strong>
                        MedAI
                    </strong>

                    <span>
                        AI Assistant
                    </span>

                </div>

                <div class="bubble">

                    <p>
                        Hello! 👋
                    </p>

                    <p>
                        I'm MedAI, your medical
                        information assistant.
                    </p>

                    <p>
                        What would you like to
                        know today?
                    </p>

                </div>

            </div>

        </div>
    `;

    messageInput.focus();
}


// ============================================================
// INITIAL FOCUS
// ============================================================

if (messageInput) {
    messageInput.focus();
}