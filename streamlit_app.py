from sqlalchemy import event
import streamlit as st
import streamlit.components.v1 as components
import requests
import json


BACKEND_HTTP = "https://mammary-related-outpost.ngrok-free.dev"
BACKEND_WS = "wss://mammary-related-outpost.ngrok-free.dev"

st.set_page_config(
    page_title="Calling App",
    page_icon="📞",
    layout="wide"
)

if "call_id" not in st.session_state:
    st.session_state.call_id = None

if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "remote_user_id" not in st.session_state:
    st.session_state.remote_user_id = ""

if "in_call" not in st.session_state:
    st.session_state.in_call = False


def create_call(user_id, remote_user_id):
    payload = {
        "call_type": "one_to_one",
        "created_by": user_id,
        "participants": [
            user_id,
            remote_user_id
        ],
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
            st.error(response.text)
            return None
        data = response.json()
        call_id = data["call"]["id"]
        return call_id

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
            st.error(response.text)
            return False
        return True

    except Exception as e:
        st.error(
            f"Unable to join call: {e}"
        )
        return False

def end_call(call_id):
    try:
        requests.post(
            f"{BACKEND_HTTP}/calls/{call_id}/end",
            timeout=10
        )
    except Exception:
        pass

st.title("📞 Calling Application")

st.caption(
    "One-to-One WebRTC Audio / Video Call"
)

with st.sidebar:
    st.header("User")
    user_id = st.text_input(
        "Your User ID",
        value=st.session_state.user_id or "user1"
    )
    remote_user_id = st.text_input(
        "Other User ID",
        value=st.session_state.remote_user_id or "user2"
    )
    st.session_state.user_id = user_id
    st.session_state.remote_user_id = remote_user_id


st.subheader("Call")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📞 Caller")
    if st.button("Create Call", use_container_width=True):
        if not user_id:
            st.error("Enter your User ID")
        elif not remote_user_id:
            st.error("Enter other user's ID")
        else:
            call_id = create_call(
                user_id,
                remote_user_id
            )
            if call_id:
                st.session_state.call_id = call_id
                joined = join_call(
                    call_id,
                    user_id
                )
                if joined:
                    st.session_state.in_call = True
                    st.success(
                        f"Call created: {call_id}"
                    )
                    st.rerun()

with col2:
    st.markdown("### 📲 Receiver")
    call_id_input = st.text_input(
        "Enter Call ID",
        value=""
    )
    if st.button("Join Call", use_container_width=True):
        if not call_id_input:
            st.error("Enter Call ID")
        elif not user_id:
            st.error("Enter your User ID")
        else:
            try:
                call_id = int(
                    call_id_input
                )
            except ValueError:
                st.error(
                    "Call ID must be a number"
                )
                call_id = None

            if call_id:
                joined = join_call(
                    call_id,
                    user_id
                )
                if joined:
                    st.session_state.call_id = call_id
                    st.session_state.in_call = True
                    st.success(f"Joined call: {call_id}")
                    st.rerun()

if st.session_state.call_id:
    st.info(
        f"Call ID: {st.session_state.call_id}"
    )

if st.session_state.in_call:
    st.subheader("🎥 Video Call")
    call_id = st.session_state.call_id
    html_code = f"""
    
<!DOCTYPE html>
<html>
<head>
<style>

body {{
    margin: 0;
    background: #111827;
    color: white;
    font-family: Arial, sans-serif;
}}
.container {{
    padding: 10px;
}}
.videos {{
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}}

.video-box {{
    width: 48%;
    min-width: 300px;
}}

video {{
    width: 100%;
    background: black;
    border-radius: 12px;
}}

.status {{
    margin: 10px 0;
    padding: 10px;
    background: #1f2937;
    border-radius: 8px;
}}

.controls {{
    display: flex;
    gap: 10px;
    margin-top: 15px;
}}

button {{
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    background: #374151;
    color: white;
}}

button:hover {{
    background: #4b5563;
}}

.end {{
    background: #dc2626;
}}

</style>
</head>
<body>

<div class="container">
<div class="status">

Status:
<span id="status">
Connecting...
</span>
</div>

<div class="videos">
<div class="video-box">
<p>Local Video</p>
<video
    id="localVideo"
    autoplay
    muted
    playsinline>
</video>
</div>

<div class="video-box">
<p>Remote Video</p>

<video
    id="remoteVideo"
    autoplay
    playsinline>
</video>
</div>
</div>

<div class="controls">
<button onclick="toggleMute()">
🎤 Mute
</button>

<button onclick="toggleCamera()">
📹 Camera
</button>
</div>
</div>

<script>
const CALL_ID = "{call_id}";
const USER_ID = "{user_id}";
const REMOTE_USER_ID = "{remote_user_id}";

const WS_URL =
    "{BACKEND_WS}/ws/calls/"
    + CALL_ID
    + "/"
    + USER_ID;

let socket = null;
let peerConnection = null;
let localStream = null;
let remoteStream = null;
let isMuted = false;
let cameraEnabled = true;
let iceCandidatesQueue = [];
let mediaReady = Promise.resolve();
let offerSent = false;

function setStatus(message) {{
    document.getElementById(
        "status"
    ).innerText = message;

}}

function createPeerConnection() {{
    peerConnection =
        new RTCPeerConnection({{
            iceServers: [
                {{
                    urls:
                    "stun:stun.l.google.com:19302"
                }}
            ]
        }});

    remoteStream = new MediaStream();

    const remoteVideo = document.getElementById("remoteVideo");
    remoteVideo.srcObject = remoteStream;

    peerConnection.ontrack =
        function(event) {{
            console.log("Remote track received:", event.track.kind);
            if (event.streams && event.streams[0]) {{
                remoteVideo.srcObject = event.streams[0];
            }} else {{
                remoteStream.addTrack(event.track);
                remoteVideo.srcObject = remoteStream;
            }}
            remoteVideo.play().catch(error =>
                console.warn("Remote video autoplay was blocked:", error)
            );
        }};

    peerConnection.onicecandidate =
        function(event) {{
            if (event.candidate) {{
                socket.send(
                    JSON.stringify({{
                        event:"ice_candidate",
                        to: REMOTE_USER_ID,
                        candidate: event.candidate.candidate,
                        sdpMid: event.candidate.sdpMid,
                        sdpMLineIndex: event.candidate.sdpMLineIndex
                    }})
                );
            }}
        }};

    peerConnection.onconnectionstatechange =
        function() {{
            console.log("WebRTC connection state:", peerConnection.connectionState);
            setStatus(
                "WebRTC: "
                + peerConnection.connectionState
            );
        }};

    peerConnection.oniceconnectionstatechange =
        function() {{
            console.log("ICE connection state:", peerConnection.iceConnectionState);
        }};
}}


async function startMedia() {{
    try {{
        localStream =
            await navigator.mediaDevices
                .getUserMedia({{
                    audio: true,
                    video: true
                }});

        document.getElementById(
            "localVideo"
        ).srcObject = localStream;

        localStream
            .getTracks()
            .forEach(track => {{
                peerConnection.addTrack(
                    track,
                    localStream
                );

            }});

    }}
    catch(error) {{
        console.error(error);
        setStatus(
            "Camera/Microphone permission denied"
        );
    }}
}}

async function processIceQueue() {{
    while (iceCandidatesQueue.length > 0) {{
        const message = iceCandidatesQueue.shift();
        await peerConnection.addIceCandidate({{
            candidate: message.candidate,
            sdpMid: message.sdpMid,
            sdpMLineIndex: message.sdpMLineIndex
        }});
    }}
}}

async function createOffer() {{
    await mediaReady;
    if (offerSent || peerConnection.signalingState !== "stable") {{
        return;
    }}
    if (peerConnection.getSenders().length === 0) {{
        setStatus("Cannot call: camera/microphone unavailable");
        return;
    }}

    const offer =
        await peerConnection.createOffer();
    await peerConnection
        .setLocalDescription(
            offer
        );
    socket.send(
        JSON.stringify({{
            event: "offer",
            target: REMOTE_USER_ID,
            sdp: offer.sdp
        }})
    );
    offerSent = true;
    setStatus(
        "Calling " + REMOTE_USER_ID
    );
}}

async function handleOffer(message) {{
    await mediaReady;
    await peerConnection
        .setRemoteDescription({{
            type: "offer",
            sdp: message.sdp
        }});

    await processIceQueue();

    const answer =
        await peerConnection
            .createAnswer();
    await peerConnection
        .setLocalDescription(
            answer
        );

    socket.send(
        JSON.stringify({{
            event: "answer",
            to: message.from,
            sdp: answer.sdp
        }})
    );
    setStatus(
        "Call connected"
    );

}}

async function handleAnswer(message) {{
    await peerConnection
        .setRemoteDescription({{
            type: "answer",
            sdp: message.sdp

        }});

    await processIceQueue();

    setStatus(
        "Call connected"
    );
}}

async function handleIceCandidate(message) {{
    if (!message.candidate) {{
        return;
    }}

    if (!peerConnection.remoteDescription) {{
        iceCandidatesQueue.push(message);
        return;
    }}

    try {{
        await peerConnection
            .addIceCandidate({{
                candidate:
                    message.candidate,
                sdpMid:
                    message.sdpMid,
                sdpMLineIndex:
                    message.sdpMLineIndex

            }});

    }}
    catch(error) {{

        console.error(
            "ICE error:",
            error
        );

    }}

}}

function connectWebSocket() {{
    socket =
        new WebSocket(
            WS_URL
        );

    socket.onopen =
        async function() {{
            setStatus(
                "Signaling connected"
            );
            createPeerConnection();
            mediaReady = startMedia();
            await mediaReady;

        }};

    socket.onmessage =
        async function(event) {{
            const message =
                JSON.parse(
                    event.data
                );
            console.log(
                "Received:",
                message
            );
            if (
                message.event
                === "user_joined"
            ) {{
                if (
                    String(message.user_id)
                    === String(REMOTE_USER_ID)
                ) {{
                    await createOffer();
                }}
            }}
            else if (
                message.event
                === "offer"
            ) {{
                await handleOffer(
                    message
                );
            }}
            else if (
                message.event
                === "answer"
            ) {{
                await handleAnswer(
                    message
                );
            }}
            else if (
                message.event
                === "ice_candidate"
            ) {{
                await handleIceCandidate(
                    message
                );
            }}
            else if (
                message.event
                === "user_left"
            ) {{
                setStatus(
                    "Other user left"
                );
            }}
        }};

    socket.onerror =
        function(error) {{
            console.error(error);
            setStatus(
                "WebSocket error"
            );
        }};

    socket.onclose =
        function() {{
            setStatus(
                "Disconnected"
            );

        }};
}}

function toggleMute() {{
    if (!localStream) {{
        return;
    }}
    const audioTracks = localStream.getAudioTracks();
    audioTracks.forEach(
        track => {{
            track.enabled = !track.enabled;
            isMuted = !track.enabled;
        }}
    );

    socket.send(
        JSON.stringify({{
            event: "mute",
            channel: "audio",
            muted: isMuted
        }})
    );
}}

function toggleCamera() {{
    if (!localStream) {{
        return;
    }}
    const videoTracks =
        localStream.getVideoTracks();

    videoTracks.forEach(
        track => {{
            track.enabled =
                !track.enabled;

            cameraEnabled =
                track.enabled;

        }}
    );

    socket.send(
        JSON.stringify({{
            event: "channel_status",
            channel: "video",
            status:
                cameraEnabled
                    ? "active"
                    : "inactive"
        }})
    );

}}

connectWebSocket();
</script>
</body>

</html>
"""
    components.html(
        html_code,
        height=650,
        scrolling=False
    )


if st.session_state.in_call:
    st.divider()
    if st.button(
        "❌ End Call",
        type="primary"
    ):
        end_call(
            st.session_state.call_id
        )
        st.session_state.in_call = False
        st.session_state.call_id = None
        st.rerun()
