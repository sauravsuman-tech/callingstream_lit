# from sqlalchemy import event
# import streamlit as st
# import streamlit.components.v1 as components
# import requests
# import json


# BACKEND_HTTP = "https://mammary-related-outpost.ngrok-free.dev"
# BACKEND_WS = "wss://mammary-related-outpost.ngrok-free.dev"

# st.set_page_config(
#     page_title="Calling App",
#     page_icon="📞",
#     layout="wide"
# )

# if "call_id" not in st.session_state:
#     st.session_state.call_id = None

# if "user_id" not in st.session_state:
#     st.session_state.user_id = ""

# if "remote_user_id" not in st.session_state:
#     st.session_state.remote_user_id = ""

# if "in_call" not in st.session_state:
#     st.session_state.in_call = False


# def create_call(user_id, remote_user_id):
#     payload = {
#         "call_type": "one_to_one",
#         "created_by": user_id,
#         "participants": [
#             user_id,
#             remote_user_id
#         ],
#         "recording": {
#             "enabled": False,
#             "audio": False,
#             "video": False
#         },
#         "transcription": False
#     }
#     try:
#         response = requests.post(
#             f"{BACKEND_HTTP}/calls",
#             json=payload,
#             timeout=10
#         )
#         if response.status_code != 200:
#             st.error(response.text)
#             return None
#         data = response.json()
#         call_id = data["call"]["id"]
#         return call_id

#     except Exception as e:
#         st.error(
#             f"Unable to create call: {e}"
#         )
#         return None


# def join_call(call_id, user_id):
#     try:
#         response = requests.post(
#             f"{BACKEND_HTTP}/calls/{call_id}/join/{user_id}",
#             timeout=10
#         )
#         if response.status_code != 200:
#             st.error(response.text)
#             return False
#         return True

#     except Exception as e:
#         st.error(
#             f"Unable to join call: {e}"
#         )
#         return False

# def end_call(call_id):
#     try:
#         requests.post(
#             f"{BACKEND_HTTP}/calls/{call_id}/end",
#             timeout=10
#         )
#     except Exception:
#         pass

# st.title("📞 Calling Application")

# st.caption(
#     "One-to-One WebRTC Audio / Video Call"
# )

# with st.sidebar:
#     st.header("User")
#     user_id = st.text_input(
#         "Your User ID",
#         value=st.session_state.user_id or "user1"
#     )
#     remote_user_id = st.text_input(
#         "Other User ID",
#         value=st.session_state.remote_user_id or "user2"
#     )
#     st.session_state.user_id = user_id
#     st.session_state.remote_user_id = remote_user_id


# st.subheader("Call")
# col1, col2 = st.columns(2)

# with col1:
#     st.markdown("### 📞 Caller")
#     if st.button("Create Call", use_container_width=True):
#         if not user_id:
#             st.error("Enter your User ID")
#         elif not remote_user_id:
#             st.error("Enter other user's ID")
#         else:
#             call_id = create_call(
#                 user_id,
#                 remote_user_id
#             )
#             if call_id:
#                 st.session_state.call_id = call_id
#                 joined = join_call(
#                     call_id,
#                     user_id
#                 )
#                 if joined:
#                     st.session_state.in_call = True
#                     st.success(
#                         f"Call created: {call_id}"
#                     )
#                     st.rerun()

# with col2:
#     st.markdown("### 📲 Receiver")
#     call_id_input = st.text_input(
#         "Enter Call ID",
#         value=""
#     )
#     if st.button("Join Call", use_container_width=True):
#         if not call_id_input:
#             st.error("Enter Call ID")
#         elif not user_id:
#             st.error("Enter your User ID")
#         else:
#             try:
#                 call_id = int(
#                     call_id_input
#                 )
#             except ValueError:
#                 st.error(
#                     "Call ID must be a number"
#                 )
#                 call_id = None

#             if call_id:
#                 joined = join_call(
#                     call_id,
#                     user_id
#                 )
#                 if joined:
#                     st.session_state.call_id = call_id
#                     st.session_state.in_call = True
#                     st.success(f"Joined call: {call_id}")
#                     st.rerun()

# if st.session_state.call_id:
#     st.info(
#         f"Call ID: {st.session_state.call_id}"
#     )

# if st.session_state.in_call:
#     st.subheader("🎥 Video Call")
#     call_id = st.session_state.call_id
#     html_code = f"""
    
# <!DOCTYPE html>
# <html>
# <head>
# <style>

# body {{
#     margin: 0;
#     background: #111827;
#     color: white;
#     font-family: Arial, sans-serif;
# }}
# .container {{
#     padding: 10px;
# }}
# .videos {{
#     display: flex;
#     gap: 15px;
#     flex-wrap: wrap;
# }}

# .video-box {{
#     width: 48%;
#     min-width: 300px;
# }}

# video {{
#     width: 100%;
#     background: black;
#     border-radius: 12px;
# }}

# .status {{
#     margin: 10px 0;
#     padding: 10px;
#     background: #1f2937;
#     border-radius: 8px;
# }}

# .controls {{
#     display: flex;
#     gap: 10px;
#     margin-top: 15px;
# }}

# button {{
#     padding: 10px 16px;
#     border: none;
#     border-radius: 8px;
#     cursor: pointer;
#     background: #374151;
#     color: white;
# }}

# button:hover {{
#     background: #4b5563;
# }}

# .end {{
#     background: #dc2626;
# }}

# </style>
# </head>
# <body>

# <div class="container">
# <div class="status">

# Status:
# <span id="status">
# Connecting...
# </span>
# </div>

# <div class="videos">
# <div class="video-box">
# <p>Local Video</p>
# <video
#     id="localVideo"
#     autoplay
#     muted
#     playsinline>
# </video>
# </div>

# <div class="video-box">
# <p>Remote Video</p>

# <video
#     id="remoteVideo"
#     autoplay
#     playsinline>
# </video>
# </div>
# </div>

# <div class="controls">
# <button onclick="toggleMute()">
# 🎤 Mute
# </button>

# <button onclick="toggleCamera()">
# 📹 Camera
# </button>
# </div>
# </div>

# <script>
# const CALL_ID = "{call_id}";
# const USER_ID = "{user_id}";
# const REMOTE_USER_ID = "{remote_user_id}";

# const WS_URL =
#     "{BACKEND_WS}/ws/calls/"
#     + CALL_ID
#     + "/"
#     + USER_ID;

# let socket = null;
# let peerConnection = null;
# let localStream = null;
# let remoteStream = null;
# let isMuted = false;
# let cameraEnabled = true;
# let iceCandidatesQueue = [];
# let mediaReady = Promise.resolve();
# let offerSent = false;

# function setStatus(message) {{
#     document.getElementById(
#         "status"
#     ).innerText = message;

# }}

# function createPeerConnection() {{
#     peerConnection =
#         new RTCPeerConnection({{
#             iceServers: [
#                 {{
#                     urls:
#                     "stun:stun.l.google.com:19302"
#                 }}
#             ]
#         }});

#     remoteStream = new MediaStream();

#     const remoteVideo = document.getElementById("remoteVideo");
#     remoteVideo.srcObject = remoteStream;

#     peerConnection.ontrack =
#         function(event) {{
#             console.log("Remote track received:", event.track.kind);
#             if (event.streams && event.streams[0]) {{
#                 remoteVideo.srcObject = event.streams[0];
#             }} else {{
#                 remoteStream.addTrack(event.track);
#                 remoteVideo.srcObject = remoteStream;
#             }}
#             remoteVideo.play().catch(error =>
#                 console.warn("Remote video autoplay was blocked:", error)
#             );
#         }};

#     peerConnection.onicecandidate =
#         function(event) {{
#             if (event.candidate) {{
#                 socket.send(
#                     JSON.stringify({{
#                         event:"ice_candidate",
#                         to: REMOTE_USER_ID,
#                         candidate: event.candidate.candidate,
#                         sdpMid: event.candidate.sdpMid,
#                         sdpMLineIndex: event.candidate.sdpMLineIndex
#                     }})
#                 );
#             }}
#         }};

#     peerConnection.onconnectionstatechange =
#         function() {{
#             console.log("WebRTC connection state:", peerConnection.connectionState);
#             setStatus(
#                 "WebRTC: "
#                 + peerConnection.connectionState
#             );
#         }};

#     peerConnection.oniceconnectionstatechange =
#         function() {{
#             console.log("ICE connection state:", peerConnection.iceConnectionState);
#         }};
# }}


# async function startMedia() {{
#     try {{
#         localStream =
#             await navigator.mediaDevices
#                 .getUserMedia({{
#                     audio: true,
#                     video: true
#                 }});

#         document.getElementById(
#             "localVideo"
#         ).srcObject = localStream;

#         localStream
#             .getTracks()
#             .forEach(track => {{
#                 peerConnection.addTrack(
#                     track,
#                     localStream
#                 );

#             }});

#     }}
#     catch(error) {{
#         console.error(error);
#         setStatus(
#             "Camera/Microphone permission denied"
#         );
#     }}
# }}

# async function processIceQueue() {{
#     while (iceCandidatesQueue.length > 0) {{
#         const message = iceCandidatesQueue.shift();
#         await peerConnection.addIceCandidate({{
#             candidate: message.candidate,
#             sdpMid: message.sdpMid,
#             sdpMLineIndex: message.sdpMLineIndex
#         }});
#     }}
# }}

# async function createOffer() {{
#     await mediaReady;
#     if (offerSent || peerConnection.signalingState !== "stable") {{
#         return;
#     }}
#     if (peerConnection.getSenders().length === 0) {{
#         setStatus("Cannot call: camera/microphone unavailable");
#         return;
#     }}

#     const offer =
#         await peerConnection.createOffer();
#     await peerConnection
#         .setLocalDescription(
#             offer
#         );
#     socket.send(
#         JSON.stringify({{
#             event: "offer",
#             target: REMOTE_USER_ID,
#             sdp: offer.sdp
#         }})
#     );
#     offerSent = true;
#     setStatus(
#         "Calling " + REMOTE_USER_ID
#     );
# }}

# async function handleOffer(message) {{
#     await mediaReady;
#     await peerConnection
#         .setRemoteDescription({{
#             type: "offer",
#             sdp: message.sdp
#         }});

#     await processIceQueue();

#     const answer =
#         await peerConnection
#             .createAnswer();
#     await peerConnection
#         .setLocalDescription(
#             answer
#         );

#     socket.send(
#         JSON.stringify({{
#             event: "answer",
#             to: message.from,
#             sdp: answer.sdp
#         }})
#     );
#     setStatus(
#         "Call connected"
#     );

# }}

# async function handleAnswer(message) {{
#     await peerConnection
#         .setRemoteDescription({{
#             type: "answer",
#             sdp: message.sdp

#         }});

#     await processIceQueue();

#     setStatus(
#         "Call connected"
#     );
# }}

# async function handleIceCandidate(message) {{
#     if (!message.candidate) {{
#         return;
#     }}

#     if (!peerConnection.remoteDescription) {{
#         iceCandidatesQueue.push(message);
#         return;
#     }}

#     try {{
#         await peerConnection
#             .addIceCandidate({{
#                 candidate:
#                     message.candidate,
#                 sdpMid:
#                     message.sdpMid,
#                 sdpMLineIndex:
#                     message.sdpMLineIndex

#             }});

#     }}
#     catch(error) {{

#         console.error(
#             "ICE error:",
#             error
#         );

#     }}

# }}

# function connectWebSocket() {{
#     socket =
#         new WebSocket(
#             WS_URL
#         );

#     socket.onopen =
#         async function() {{
#             setStatus(
#                 "Signaling connected"
#             );
#             createPeerConnection();
#             mediaReady = startMedia();
#             await mediaReady;

#         }};

#     socket.onmessage =
#         async function(event) {{
#             const message =
#                 JSON.parse(
#                     event.data
#                 );
#             console.log(
#                 "Received:",
#                 message
#             );
#             if (
#                 message.event
#                 === "user_joined"
#             ) {{
#                 if (
#                     String(message.user_id)
#                     === String(REMOTE_USER_ID)
#                 ) {{
#                     await createOffer();
#                 }}
#             }}
#             else if (
#                 message.event
#                 === "offer"
#             ) {{
#                 await handleOffer(
#                     message
#                 );
#             }}
#             else if (
#                 message.event
#                 === "answer"
#             ) {{
#                 await handleAnswer(
#                     message
#                 );
#             }}
#             else if (
#                 message.event
#                 === "ice_candidate"
#             ) {{
#                 await handleIceCandidate(
#                     message
#                 );
#             }}
#             else if (
#                 message.event
#                 === "user_left"
#             ) {{
#                 setStatus(
#                     "Other user left"
#                 );
#             }}
#         }};

#     socket.onerror =
#         function(error) {{
#             console.error(error);
#             setStatus(
#                 "WebSocket error"
#             );
#         }};

#     socket.onclose =
#         function() {{
#             setStatus(
#                 "Disconnected"
#             );

#         }};
# }}

# function toggleMute() {{
#     if (!localStream) {{
#         return;
#     }}
#     const audioTracks = localStream.getAudioTracks();
#     audioTracks.forEach(
#         track => {{
#             track.enabled = !track.enabled;
#             isMuted = !track.enabled;
#         }}
#     );

#     socket.send(
#         JSON.stringify({{
#             event: "mute",
#             channel: "audio",
#             muted: isMuted
#         }})
#     );
# }}

# function toggleCamera() {{
#     if (!localStream) {{
#         return;
#     }}
#     const videoTracks =
#         localStream.getVideoTracks();

#     videoTracks.forEach(
#         track => {{
#             track.enabled =
#                 !track.enabled;

#             cameraEnabled =
#                 track.enabled;

#         }}
#     );

#     socket.send(
#         JSON.stringify({{
#             event: "channel_status",
#             channel: "video",
#             status:
#                 cameraEnabled
#                     ? "active"
#                     : "inactive"
#         }})
#     );

# }}

# connectWebSocket();
# </script>
# </body>

# </html>
# """
#     components.html(
#         html_code,
#         height=650,
#         scrolling=False
#     )


# if st.session_state.in_call:
#     st.divider()
#     if st.button(
#         "❌ End Call",
#         type="primary"
#     ):
#         end_call(
#             st.session_state.call_id
#         )
#         st.session_state.in_call = False
#         st.session_state.call_id = None
#         st.rerun()




import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import html


BACKEND_HTTP = "https://mammary-related-outpost.ngrok-free.dev"
BACKEND_WS = "ws://mammary-related-outpost.ngrok-free.dev"


st.set_page_config(
    page_title="WebRTC Calling",
    page_icon="📞",
    layout="wide",
)

if "call_id" not in st.session_state:
    st.session_state.call_id = None

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "call_type" not in st.session_state:
    st.session_state.call_type = "one_to_one"

if "in_call" not in st.session_state:
    st.session_state.in_call = False


def create_call(user_id, call_type, participants):

    payload = {
        "call_type": call_type,
        "created_by": user_id,
        "participants": participants,

        "recording": {
            "enabled": False,
            "audio": False,
            "video": False
        },

        "transcription": False
    }

    try:
        response = requests.post(
            f"{BACKEND_HTTP}/calls",
            json=payload,
            timeout=10
        )

        if response.status_code != 200:

            st.error(
                f"Create call failed:\n{response.text}"
            )

            return None
        data = response.json()
        return data["call"]["id"]

    except Exception as e:
        st.error(
            f"Unable to create call: {e}"
        )
        return None


def join_call(call_id, user_id):
    try:
        response = requests.post(
            f"{BACKEND_HTTP}/calls/{call_id}/join/{user_id}",
            timeout=10
        )

        if response.status_code != 200:
            st.error(
                f"Join call failed:\n{response.text}"
            )
            return False
        return True

    except Exception as e:
        st.error(
            f"Unable to join call: {e}"
        )
        return False


def end_call(call_id):
    try:
        response = requests.post(
            f"{BACKEND_HTTP}/calls/{call_id}/end",
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False


st.title("📞 WebRTC Calling Application")
st.caption(
    "One-to-One / One-to-Many / Many-to-Many"
)

with st.sidebar:
    st.header("👤 User")
    user_id = st.text_input(
        "Your User ID",
        value=st.session_state.user_id or "user1"
    )
    call_types = [
        "one_to_one",
        "one_to_many",
        "many_to_many"
    ]

    current_index = call_types.index(
        st.session_state.call_type
    )

    call_type = st.selectbox(
        "Call Type",
        call_types,
        index=current_index
    )

    st.session_state.user_id = user_id
    st.session_state.call_type = call_type

    st.divider()

    st.markdown("### Call types")

    st.markdown(
        """
        **One-to-One**

        Exactly 2 users.

        **One-to-Many**

        1 host + multiple participants.

        **Many-to-Many**

        Multiple users can send and receive video.
        """
    )

st.subheader("Call")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📞 Create Call")
    participant_text = st.text_input(
        "Participants",
        value="user1,user2",
        help="Enter comma-separated User IDs."
    )

    st.caption(
        "Example: user1,user2,user3,user4"
    )

    if st.button(
        "Create Call",
        use_container_width=True
    ):

        clean_user_id = user_id.strip()

        if not clean_user_id:

            st.error(
                "Enter your User ID"
            )

        else:

            # ------------------------------------------------
            # Parse participants
            # ------------------------------------------------

            participants = [
                item.strip()
                for item in participant_text.split(",")
                if item.strip()
            ]

            # Remove duplicates while preserving order

            participants = list(
                dict.fromkeys(participants)
            )

            # Creator must always be included

            if clean_user_id not in participants:

                participants.insert(
                    0,
                    clean_user_id
                )

            # ------------------------------------------------
            # Validate call type
            # ------------------------------------------------

            if call_type == "one_to_one":
                if len(participants) != 2:

                    st.error(
                        "One-to-One call requires exactly 2 participants."
                    )
                    st.stop()

            elif call_type == "one_to_many":
                if len(participants) < 2:
                    st.error(
                        "One-to-Many call requires at least 2 participants."
                    )
                    st.stop()

            elif call_type == "many_to_many":
                if len(participants) < 2:

                    st.error(
                        "Many-to-Many call requires at least 2 participants."
                    )
                    st.stop()

            # ------------------------------------------------
            # Create call
            # ------------------------------------------------

            call_id = create_call(
                clean_user_id,
                call_type,
                participants
            )

            if call_id is not None:
                st.session_state.call_id = call_id
                st.session_state.in_call = True

                st.success(
                    f"Call created: {call_id}"
                )

                st.info(
                    "Participants: "
                    + ", ".join(participants)
                )
                st.rerun()


with col2:

    st.markdown("### 🔗 Join Call")

    join_call_id = st.text_input(
        "Call ID",
        value=""
    )

    if st.button(
        "Join Call",
        use_container_width=True
    ):

        clean_user_id = user_id.strip()
        clean_call_id = join_call_id.strip()

        if not clean_user_id:
            st.error(
                "Enter your User ID"
            )
        elif not clean_call_id:
            st.error(
                "Enter Call ID"
            )

        else:
            success = join_call(
                clean_call_id,
                clean_user_id
            )

            if success:

                st.session_state.call_id = (
                    clean_call_id
                )

                st.session_state.in_call = True

                st.success(
                    "Joined call successfully"
                )
                st.rerun()

# ============================================================
# CALL INFO
# ============================================================

if st.session_state.in_call:
    st.divider()
    st.success(
        f"Connected to Call: "
        f"{st.session_state.call_id}"
    )
    st.info(
        f"User: {st.session_state.user_id} | "
        f"Type: {st.session_state.call_type}"
    )


# ============================================================
# WEBRTC UI
# ============================================================

if (
    st.session_state.in_call
    and st.session_state.call_id
    and st.session_state.user_id
):

    call_id = str(
        st.session_state.call_id
    )

    current_user_id = str(
        st.session_state.user_id
    )

    ws_url = (
        f"{BACKEND_WS}"
        f"/ws/calls/"
        f"{call_id}/"
        f"{current_user_id}"
    )

    # Escape values before injecting into HTML/JS

    safe_user_id = json.dumps(
        current_user_id
    )

    safe_ws_url = json.dumps(
        ws_url
    )

    html_code = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">
<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 10px;

    background: #111;
    color: white;

    font-family: Arial, sans-serif;
}}

#status {{
    padding: 10px;
    margin-bottom: 10px;

    background: #222;

    border-radius: 8px;

    font-size: 14px;
}}

#videos {{
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(280px, 1fr)
        );

    gap: 12px;
}}

#remoteVideos {{
    display: contents;
}}

.video-box {{
    position: relative;

    background: #000;

    border-radius: 10px;

    overflow: hidden;

    min-height: 220px;
}}

.video-box video {{
    width: 100%;
    height: 100%;

    min-height: 220px;

    object-fit: cover;

    background: #000;
}}

.video-label {{
    position: absolute;

    left: 8px;
    bottom: 8px;

    padding: 5px 9px;

    background: rgba(0,0,0,0.65);

    border-radius: 5px;

    font-size: 13px;
}}

#controls {{
    display: flex;

    gap: 10px;

    margin-top: 15px;

    flex-wrap: wrap;
}}

button {{
    padding: 10px 18px;

    border: none;

    border-radius: 7px;

    cursor: pointer;

    font-size: 14px;
}}

</style>

</head>


<body>


<div id="status">
    Connecting...
</div>


<div id="videos">

    <!-- LOCAL VIDEO -->

    <div class="video-box">

        <video
            id="localVideo"
            autoplay
            muted
            playsinline>
        </video>

        <div class="video-label">
            You ({current_user_id})
        </div>

    </div>


    <!-- REMOTE VIDEOS -->

    <div id="remoteVideos"></div>

</div>


<div id="controls">

    <button onclick="toggleMute()">
        🎤 Mute
    </button>

    <button onclick="toggleCamera()">
        📷 Camera
    </button>

</div>


<script>


// ============================================================
// GLOBAL STATE
// ============================================================

const USER_ID = {safe_user_id};

const WS_URL = {safe_ws_url};

let socket = null;

let localStream = null;


// IMPORTANT:
// One RTCPeerConnection per remote user.
//
// Example:
//
// user1 -> user2
// user1 -> user3
// user1 -> user4
//
// This is P2P mesh.

const peerConnections = {{}};
const remoteStreams = {{}};
const iceQueues = {{}};


console.log(
    "USER_ID:",
    USER_ID
);

console.log(
    "WS_URL:",
    WS_URL
);


// ============================================================
// STATUS
// ============================================================

function setStatus(message) {{

    const element =
        document.getElementById("status");

    if (element) {{

        element.innerText = message;

    }}

}}


// ============================================================
// CREATE REMOTE VIDEO
// ============================================================

function createRemoteVideo(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    const existing =
        document.getElementById(
            "video-box-" + remoteUserId
        );


    if (existing) {{

        return;

    }}


    const container =
        document.getElementById(
            "remoteVideos"
        );


    const box =
        document.createElement(
            "div"
        );


    box.className =
        "video-box";


    box.id =
        "video-box-" +
        remoteUserId;


    const video =
        document.createElement(
            "video"
        );


    video.id =
        "remote-" +
        remoteUserId;


    video.autoplay = true;

    video.playsInline = true;


    const label =
        document.createElement(
            "div"
        );


    label.className =
        "video-label";


    label.innerText =
        remoteUserId;


    box.appendChild(video);

    box.appendChild(label);

    container.appendChild(box);

}}


function removeRemoteVideo(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    const box =
        document.getElementById(
            "video-box-" +
            remoteUserId
        );


    if (box) {{

        box.remove();

    }}

}}


// ============================================================
// CREATE PEER CONNECTION
// ============================================================

function createPeerConnection(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    if (
        peerConnections[remoteUserId]
    ) {{

        return peerConnections[
            remoteUserId
        ];

    }}


    console.log(
        "Creating peer connection:",
        remoteUserId
    );


    const pc =
        new RTCPeerConnection({{

            iceServers: [

                {{
                    urls:
                        "stun:stun.l.google.com:19302"
                }}

            ]

        }});


    peerConnections[
        remoteUserId
    ] = pc;


    remoteStreams[
        remoteUserId
    ] = new MediaStream();


    iceQueues[
        remoteUserId
    ] = [];


    createRemoteVideo(
        remoteUserId
    );


    const remoteVideo =
        document.getElementById(
            "remote-" +
            remoteUserId
        );


    // ========================================================
    // LOCAL TRACKS
    // ========================================================

    if (localStream) {{

        localStream
            .getTracks()
            .forEach(
                function(track) {{

                    pc.addTrack(
                        track,
                        localStream
                    );

                }}
            );

    }}


    // ========================================================
    // REMOTE TRACKS
    // ========================================================

    pc.ontrack =
        function(event) {{

            console.log(
                "Remote track:",
                remoteUserId,
                event.track.kind
            );


            if (
                event.streams &&
                event.streams.length > 0
            ) {{

                remoteVideo.srcObject =
                    event.streams[0];

            }}
            else {{

                const stream =
                    remoteStreams[
                        remoteUserId
                    ];

                stream.addTrack(
                    event.track
                );

                remoteVideo.srcObject =
                    stream;

            }}


            remoteVideo
                .play()
                .catch(
                    function() {{}}
                );

        }};


    // ========================================================
    // ICE CANDIDATE
    // ========================================================

    pc.onicecandidate =
        function(event) {{

            if (!event.candidate) {{

                return;

            }}


            if (
                socket &&
                socket.readyState ===
                WebSocket.OPEN
            ){{

                socket.send(
                    JSON.stringify({{

                        event:
                            "ice_candidate",

                        to:
                            remoteUserId,

                        candidate:
                            event.candidate.candidate,

                        sdpMid:
                            event.candidate.sdpMid,

                        sdpMLineIndex:
                            event.candidate.sdpMLineIndex

                    }})
                );

            }}

        }};


    // ========================================================
    // CONNECTION STATE
    // ========================================================

    pc.onconnectionstatechange =
        function() {{

            console.log(
                "Connection state:",
                remoteUserId,
                pc.connectionState
            );


            if (
                pc.connectionState ===
                "connected"
            ) {{

                console.log(
                    "WebRTC connected:",
                    remoteUserId
                );

            }}


            if (
                pc.connectionState ===
                "failed"
            ) {{

                console.log(
                    "Peer failed:",
                    remoteUserId
                );

            }}


            if (
                pc.connectionState ===
                "disconnected"
            ) {{

                console.log(
                    "Peer disconnected:",
                    remoteUserId
                );

            }}

        }};

    pc.oniceconnectionstatechange =
        function() {{

            console.log(
                "ICE state:",
                remoteUserId,
                pc.iceConnectionState
            );

        }};


    return pc;

}}


async function createOffer(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    // Never connect to ourselves

    if (
        remoteUserId ===
        String(USER_ID)
    ) {{

        return;

    }}


    // Existing connection

    if (
        peerConnections[
            remoteUserId
        ]
    ) {{

        console.log(
            "Peer already exists:",
            remoteUserId
        );

        return;

    }}


    if (
        !socket ||
        socket.readyState !==
        WebSocket.OPEN
    ) {{

        console.warn(
            "WebSocket not ready"
        );

        return;

    }}


    const pc =
        createPeerConnection(
            remoteUserId
        );


    try {{

        const offer =
            await pc.createOffer();


        await pc.setLocalDescription(
            offer
        );


        socket.send(
            JSON.stringify({{

                event:
                    "offer",

                target:
                    remoteUserId,

                sdp:
                    offer.sdp

            }})
        );


        console.log(
            "Offer sent:",
            remoteUserId
        );

    }}
    catch(error) {{

        console.error(
            "Offer error:",
            error
        );

    }}

}}

// HANDLE OFFER

async function handleOffer(message) {{
    const remoteUserId =
        String(
            message.from
        );

    const pc =
        createPeerConnection(
            remoteUserId
        );

    try {{
        await pc.setRemoteDescription({{
            type: "offer",
            sdp: message.sdp
        }});


        await flushIceQueue(
            remoteUserId
        );


        const answer =
            await pc.createAnswer();

        await pc.setLocalDescription(
            answer
        );

        socket.send(
            JSON.stringify({{
                event:
                    "answer",
                to:
                    remoteUserId,

                sdp:
                    answer.sdp
            }})
        );


        console.log(
            "Answer sent:",
            remoteUserId
        );

    }}
    catch(error) {{

        console.error(
            "Offer handling error:",
            error
        );

    }}

}}


// HANDLE ANSWER

async function handleAnswer(message) {{
    const remoteUserId =
        String(
            message.from
        );

    const pc =
        peerConnections[
            remoteUserId
        ];

    if (!pc) {{
        console.warn(
            "No peer for answer:",
            remoteUserId
        );
        return;

    }}

    try {{
        await pc.setRemoteDescription({{
            type:
                "answer",
            sdp:
                message.sdp

        }});


        await flushIceQueue(
            remoteUserId
        );

        console.log(
            "Answer received:",
            remoteUserId
        );

    }}
    catch(error) {{
        console.error(
            "Answer error:",
            error
        );

    }}

}}

// HANDLE ICE CANDIDATE

async function handleIceCandidate(message) {{
    const remoteUserId =
        String(
            message.from
        );

    const pc =
        createPeerConnection(
            remoteUserId
        );

    if (!message.candidate) {{
        return;

    }}

    const candidate = {{
        candidate:
            message.candidate,

        sdpMid:
            message.sdpMid,

        sdpMLineIndex:
            message.sdpMLineIndex

    }};


    // Remote SDP not ready yet.
    // Queue candidate.

    if (!pc.remoteDescription) {{
        if (
            !iceQueues[
                remoteUserId
            ]
        ) {{

            iceQueues[
                remoteUserId
            ] = [];

        }}


        iceQueues[
            remoteUserId
        ].push(candidate);


        console.log(
            "ICE queued:",
            remoteUserId
        );

        return;

    }}


    try {{

        await pc.addIceCandidate(
            candidate
        );

    }}
    catch(error) {{

        console.error(
            "ICE error:",
            remoteUserId,
            error
        );

    }}

}}

async function flushIceQueue(remoteUserId) {{
    remoteUserId =
        String(remoteUserId);

    const pc =
        peerConnections[
            remoteUserId
        ];


    if (!pc) {{

        return;

    }}


    if (!pc.remoteDescription) {{

        return;

    }}


    const queue =
        iceQueues[
            remoteUserId
        ] || [];


    while (
        queue.length > 0
    ) {{

        const candidate =
            queue.shift();


        try {{

            await pc.addIceCandidate(
                candidate
            );

        }}
        catch(error) {{

            console.error(
                "Queued ICE error:",
                remoteUserId,
                error
            );

        }}

    }}

}}


function closePeer(remoteUserId) {{
    remoteUserId =
        String(remoteUserId);

    const pc =
        peerConnections[
            remoteUserId
        ];

    if (pc) {{
        pc.close();

        delete peerConnections[
            remoteUserId
        ];

    }}


    delete remoteStreams[
        remoteUserId
    ];


    delete iceQueues[
        remoteUserId
    ];


    removeRemoteVideo(
        remoteUserId
    );

}}


async function startMedia() {{
    try {{
        localStream =
            await navigator
                .mediaDevices
                .getUserMedia({{

                    audio:
                        true,

                    video:
                        true

                }});


        const localVideo =
            document.getElementById(
                "localVideo"
            );


        localVideo.srcObject =
            localStream;


        localVideo
            .play()
            .catch(
                function() {{}}
            );


        console.log(
            "Local media started"
        );


        return true;

    }}
    catch(error) {{

        console.error(
            "getUserMedia error:",
            error
        );


        setStatus(
            "Camera/microphone permission denied"
        );


        return false;

    }}

}}

function connectWebSocket() {{
    console.log(
        "Connecting WebSocket:",
        WS_URL
    );

    socket =
        new WebSocket(
            WS_URL
        );

    socket.onopen =
        async function() {{

            console.log(
                "WebSocket connected"
            );

            setStatus(
                "Signaling connected"
            );

            const mediaStarted =
                await startMedia();

            if (!mediaStarted) {{
                return;

            }}


            // Ask backend for currently
            // connected users.

            socket.send(
                JSON.stringify({{

                    event:
                        "get_users"

                }})
            );

        }};

        
    socket.onmessage =
        async function(event) {{

            const message =
                JSON.parse(
                    event.data
                );
            console.log(
                "WS message:",
                message
            );

            if (
                message.event ===
                "existing_users"
            ) {{

                const users =
                    message.users || [];


                console.log(
                    "Existing users:",
                    users
                );


                /*
                 *
                 * IMPORTANT:
                 *
                 * Do NOT create offers here.
                 *
                 * Existing users will receive
                 * user_joined when this user joins.
                 *
                 */

                return;

            }}

            if (
                message.event ===
                "user_joined"
            ) {{

                const remoteUserId =
                    String(
                        message.user_id
                    );

                if (
                    remoteUserId ===
                    String(USER_ID)
                ) {{

                    return;

                }}

                console.log(
                    "New user joined:",
                    remoteUserId
                );

                /*
                 *
                 * Existing user creates offer
                 * to newly joined user.
                 *
                 */

                await createOffer(
                    remoteUserId
                );
                return;

            }}

            if (
                message.event ===
                "offer"
            ) {{

                await handleOffer(
                    message
                );

                return;

            }}

            if (
                message.event ===
                "answer"
            ) {{

                await handleAnswer(
                    message
                );

                return;

            }}

            if (
                message.event ===
                "ice_candidate"
            ) {{

                await handleIceCandidate(
                    message
                );

                return;

            }}

            if (
                message.event ===
                "user_left"
            ) {{

                const remoteUserId =
                    String(
                        message.user_id
                    );


                closePeer(
                    remoteUserId
                );

                setStatus(
                    remoteUserId +
                    " left the call"
                );


                return;

            }}

            if (
                message.event ===
                "mute"
            ) {{

                console.log(
                    message.user_id,
                    "muted:",
                    message.muted
                );


                return;

            }}

            if (
                message.event ===
                "channel_status"
            ){{

                console.log(
                    "Channel:",
                    message.user_id,
                    message.channel,
                    message.status
                );

                return;

            }}

            if (
                message.event ===
                "recording_status"
            ) {{

                console.log(
                    "Recording:",
                    message.user_id,
                    message.status
                );

                return;

            }}

            if (
                message.event ===
                "stt_status"
            ) {{
                console.log(
                    "STT:",
                    message.user_id,
                    message.status
                );

                return;

            }}

        }};


    // ========================================================
    // ERROR
    // ========================================================

    socket.onerror =
        function(error) {{

            console.error(
                "WebSocket error:",
                error
            );


            setStatus(
                "WebSocket error"
            );

        }};


    // CLOSE

    socket.onclose =
        function(event) {{

            console.log(
                "WebSocket closed:",
                event.code,
                event.reason
            );


            setStatus(
                "Disconnected"
            );

        }};

}}

// MUTE

function toggleMute() {{
    if (!localStream) {{
        return;

    }}

    const audioTracks =
        localStream.getAudioTracks();


    audioTracks.forEach(
        function(track) {{

            track.enabled =
                !track.enabled;

        }}
    );


    const muted =
        audioTracks.length > 0
            ? !audioTracks[0].enabled
            : false;


    if (
        socket &&
        socket.readyState ===
        WebSocket.OPEN
    ) {{

        socket.send(
            JSON.stringify({{

                event:
                    "mute",

                channel:
                    "audio",

                muted:
                    muted

            }})
        );

    }}

}}


// CAMERA

function toggleCamera() {{
    if (!localStream) {{
        return;

    }}

    const videoTracks =
        localStream.getVideoTracks();

    videoTracks.forEach(
        function(track) {{

            track.enabled =
                !track.enabled;

        }}
    );


    const enabled =
        videoTracks.length > 0
            ? videoTracks[0].enabled
            : false;


    if (
        socket &&
        socket.readyState ===
        WebSocket.OPEN
    ) {{

        socket.send(
            JSON.stringify({{

                event:
                    "channel_status",

                channel:
                    "video",

                status:
                    enabled
                        ? "active"
                        : "inactive"

            }})
        );

    }}

}}


// START

connectWebSocket();
</script>
</body>

</html>
"""
    components.html(
        html_code,
        height=720,
        scrolling=False
    )

if st.session_state.in_call:
    st.divider()
    if st.button(
        "❌ End Call",
        type="primary",
        use_container_width=True
    ):
        end_call(
            st.session_state.call_id
        )
        st.session_state.in_call = False
        st.session_state.call_id = None
        st.rerun()
