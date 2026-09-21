import json
import requests
import streamlit as st
import streamlit.components.v1 as components


BACKEND_HTTP = "https://mammary-related-outpost.ngrok-free.dev"
BACKEND_WS = "wss://mammary-related-outpost.ngrok-free.dev"


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
            "video": False,
        },
        "transcription": False,
    }

    try:
        response = requests.post(
            f"{BACKEND_HTTP}/calls",
            json=payload,
            timeout=10,
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
            timeout=10,
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
            timeout=10,
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
        value=st.session_state.user_id or "user1",
    )

    call_types = [
        "one_to_one",
        "one_to_many",
        "many_to_many",
    ]

    current_index = call_types.index(
        st.session_state.call_type
    )

    call_type = st.selectbox(
        "Call Type",
        call_types,
        index=current_index,
    )

    st.session_state.user_id = user_id
    st.session_state.call_type = call_type

    st.divider()

    st.markdown("### Call types")

st.subheader("Call")

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 📞 Create Call")

    participant_text = st.text_input(
        "Participants",
        value="user1,user2",
        help="Enter comma-separated User IDs.",
    )

    st.caption(
        "Example: user1,user2,user3,user4"
    )

    if st.button(
        "Create Call",
        use_container_width=True,
    ):

        clean_user_id = user_id.strip()

        if not clean_user_id:

            st.error(
                "Enter your User ID"
            )

        else:

            participants = [
                item.strip()
                for item in participant_text.split(",")
                if item.strip()
            ]

            # Remove duplicates
            participants = list(
                dict.fromkeys(participants)
            )

            # Creator must be included
            if clean_user_id not in participants:

                participants.insert(
                    0,
                    clean_user_id,
                )

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

            call_id = create_call(
                clean_user_id,
                call_type,
                participants,
            )

            if call_id is not None:

                # Creator joins immediately
                joined = join_call(
                    call_id,
                    clean_user_id,
                )

                if joined:

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
        value="",
    )

    if st.button(
        "Join Call",
        use_container_width=True,
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
                clean_user_id,
            )

            if success:

                st.session_state.call_id = clean_call_id
                st.session_state.in_call = True

                st.success(
                    f"Joined call: {clean_call_id}"
                )
                st.rerun()

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

const USER_ID = {safe_user_id};

const WS_URL = {safe_ws_url};


console.log(
    "USER_ID:",
    USER_ID
);

console.log(
    "WS_URL:",
    WS_URL
);

let socket = null;
let localStream = null;
const peerConnections = {{}};
const remoteStreams = {{}};
const iceQueues = {{}};

function setStatus(message) {{

    const element =
        document.getElementById("status");

    if (element) {{

        element.innerText = message;

    }}

}}

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

    if (!container) {{

        return;

    }}

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
            "video-box-" + remoteUserId
        );

    if (box) {{

        box.remove();

    }}

}}

function createPeerConnection(remoteUserId) {{
    remoteUserId =
        String(remoteUserId);


    if (
        peerConnections[remoteUserId]
    ) {{

        return peerConnections[remoteUserId];

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


    peerConnections[remoteUserId] = pc;

    remoteStreams[remoteUserId] =
        new MediaStream();

    iceQueues[remoteUserId] = [];


    createRemoteVideo(
        remoteUserId
    );


    const remoteVideo =
        document.getElementById(
            "remote-" + remoteUserId
        );

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

                remoteStreams[remoteUserId]
                    .addTrack(
                        event.track
                    );

                remoteVideo.srcObject =
                    remoteStreams[remoteUserId];

            }}


            remoteVideo
                .play()
                .catch(
                    function(error) {{

                        console.warn(
                            "Remote video play failed:",
                            error
                        );

                    }}
                );

        }};

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
                const candidate = {{
                
                    event: "ice_candidate",
                    to: remoteUserId,
                    candidate: event.candidate.candidate,
                    sdpMid: event.candidate.sdpMid,
                    sdpMLineIndex: event.candidate.sdpMLineIndex
                }}
                console.log(
                    "Sending ICE:",
                    USER_ID,
                    "->",
                    remoteuserId,
                    candidate
                );
                socket.send(
                    JSON.stringify(candidate)
                )
            }}

        }};

    pc.onconnectionstatechange =
        function() {{

            console.log(
                "WebRTC:",
                remoteUserId,
                pc.connectionState
            );


            if (
                pc.connectionState ===
                "connected"
            ) {{

                setStatus(
                    "Call connected with: "
                    + remoteUserId
                );

            }}


            if (
                pc.connectionState ===
                "failed"
            ) {{

                console.error(
                    "Peer failed:",
                    remoteUserId
                );

                setStatus(
                    "WebRTC connection failed"
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

    if (
        remoteUserId ===
        String(USER_ID)
    ) {{

        return;

    }}

    if (
        peerConnections[remoteUserId]
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
            "WebSocket is not open"
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
            USER_ID,
            "->",
            remoteUserId
        );


        setStatus(
            "Calling " + remoteUserId
        );

    }}
    catch(error) {{

        console.error(
            "Offer error:",
            error
        );

    }}

}}

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

            type:
                "offer",

            sdp:
                message.sdp

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
            USER_ID,
            "->",
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
            "No peer connection for answer:",
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


        setStatus(
            "Call connected"
        );

    }}
    catch(error) {{

        console.error(
            "Answer error:",
            error
        );

    }}

}}

async function handleIceCandidate(message) {{
    const remoteUserId =
        String(
            message.from
        );


    if (!message.candidate) {{
        return;

    }}

    const pc =
        createPeerConnection(
            remoteUserId
        );

    const candidate = {{
        candidate: message.candidate,
        sdpMid: message.sdpMid,
        sdpMLineIndex: message.sdpMLineIndex

    }};
    #new code for checking
    console.log(
        "REceived ICE:",
        USER_ID,
        "<-",
        remoteUserId
    );

    if (!pc.remoteDescription) {{
        iceQueues[remoteUserId]
            .push(candidate);

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
        console.log("ICE added:", remoteUserId);

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
        iceQueues[remoteUserId] || [];


    while (
        queue.length > 0
    ){{

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
        console.log(
            "Requesting camera/microphone..."
        );

        localStream =
            await navigator
                .mediaDevices
                .getUserMedia({{

                    audio: true,

                    video: true

                }});

        const localVideo =
            document.getElementById(
                "localVideo"
            );

        localVideo.srcObject =
            localStream;

        await localVideo
            .play()
            .catch(
                function(error) {{

                    console.warn(
                        "Local video play failed:",
                        error
                    );

                }}
            );

        console.log(
            "Local media started"
        );


        setStatus(
            "Camera and microphone ready"
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

    setStatus(
        "Connecting signaling..."
    );


    socket =
        new WebSocket(
            WS_URL
        );

    socket.onopen =
        async function() {{

            console.log(
                "WebSocket connected:",
                USER_ID
            );

            setStatus(
                "Signaling connected"
            );

            const mediaStarted =
                await startMedia();

            if (!mediaStarted) {{

                return;

            }}

            socket.send(
                JSON.stringify({{

                    event:
                        "get_users"

                }})
            );

        }};

    socket.onmessage =
        async function(event) {{

            try {{

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
                ){{

                    const users =
                        message.users || [];


                    console.log(
                        "Existing users:",
                        users
                    );


                    for (
                        const remoteUserId
                        of users
                    ){{

                        if (
                            String(remoteUserId) !==
                            String(USER_ID)
                        ){{

                            await createOffer(
                                remoteUserId
                            );

                        }}

                    }}


                    return;

                }}

                if (
                    message.event ===
                    "user_joined"
                ){{

                    const remoteUserId =
                        String(
                            message.user_id
                        );


                    if (
                        remoteUserId ===
                        String(USER_ID)
                    ){{

                        return;

                    }}


                    console.log(
                        "New user joined:",
                        remoteUserId
                    );
                    return;

                }}

                if (
                    message.event ===
                    "offer"
                ){{

                    await handleOffer(
                        message
                    );

                    return;

                }}

                if (
                    message.event ===
                    "answer"
                ){{

                    await handleAnswer(
                        message
                    );

                    return;

                }}

                if (
                    message.event ===
                    "ice_candidate"
                ){{

                    await handleIceCandidate(
                        message
                    );

                    return;

                }}

                if (
                    message.event ===
                    "user_left"
                ){{

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
                ){{

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
                ){{

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
                ){{

                    console.log(
                        "STT:",
                        message.user_id,
                        message.status
                    );
                    return;

                }}

            }}
            catch(error) {{

                console.error(
                    "WebSocket message error:",
                    error
                );

            }}

        }};

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
    ){{

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
    ){{

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

connectWebSocket();

</script>
</body>

</html>
"""
    components.html(
        html_code,
        height=720,
        scrolling=False,
    )

if st.session_state.in_call:

    st.divider()

    if st.button(
        "❌ End Call",
        type="primary",
        use_container_width=True,
    ):

        end_call(
            st.session_state.call_id
        )

        st.session_state.in_call = False
        st.session_state.call_id = None

        st.rerun()
