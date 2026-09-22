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

        data = response.json()

        # Backend should return success=True
        if data.get("success") is False:
            st.error(
                data.get("message", "Unable to join call")
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
    # st.markdown("### Call types")
    # st.markdown(
    #     """
    #     **One-to-One**

    #     Exactly 2 users.

    #     **One-to-Many**

    #     1 host + multiple participants.

    #     **Many-to-Many**

    #     Multiple users can send and receive video.
    #     """
    # )


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

            # ----------------------------------------
            # CREATE CALL
            # ----------------------------------------

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


# ============================================================
# JOIN CALL
# ============================================================

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


# ============================================================
# CALL INFORMATION
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

    # --------------------------------------------------------
    # WebSocket URL
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # HTML + JavaScript
    # --------------------------------------------------------

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
    grid-template-columns: repeat(
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
}}

button {{
    padding: 10px 18px;
    border: none;
    border-radius: 7px;
    cursor: pointer;
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


console.log("====================================");
console.log("WEBRTC CLIENT START");
console.log("USER_ID:", USER_ID);
console.log("WS_URL:", WS_URL);
console.log("====================================");


let socket = null;

let localStream = null;


/*
============================================================
MEDIA READY PROMISE
============================================================

IMPORTANT:

Backend immediately sends "existing_users" after WebSocket
connection.

That message can arrive BEFORE getUserMedia() finishes.

So we create a promise and force all signaling actions
to wait until local audio/video tracks exist.
============================================================
*/

let mediaReadyPromise = Promise.resolve(false);


/*
============================================================
ONE PEER CONNECTION PER REMOTE USER
============================================================
*/

const peerConnections = {{}};


/*
============================================================
ICE QUEUES
============================================================
*/

const iceQueues = {{}};


/*
============================================================
REMOTE STREAMS
============================================================
*/

const remoteStreams = {{}};


/*
============================================================
OFFER STATE
============================================================
*/

const makingOffer = {{}};


/*
============================================================
STATUS
============================================================
*/

function setStatus(message) {{

    const el =
        document.getElementById("status");

    if (el) {{

        el.innerText = message;

    }}

}}


/*
============================================================
CREATE REMOTE VIDEO
============================================================
*/

function createRemoteVideo(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    let box =
        document.getElementById(
            "video-box-" + remoteUserId
        );


    if (box) {{

        return document.getElementById(
            "remote-" + remoteUserId
        );

    }}


    const container =
        document.getElementById(
            "remoteVideos"
        );


    if (!container) {{

        console.error(
            "Remote video container not found"
        );

        return null;

    }}


    box =
        document.createElement("div");

    box.className =
        "video-box";

    box.id =
        "video-box-" + remoteUserId;


    const video =
        document.createElement("video");


    video.id =
        "remote-" + remoteUserId;

    video.autoplay = true;

    video.playsInline = true;

    video.controls = false;


    const label =
        document.createElement("div");


    label.className =
        "video-label";

    label.innerText =
        remoteUserId;


    box.appendChild(video);

    box.appendChild(label);

    container.appendChild(box);


    console.log(
        "REMOTE VIDEO CREATED:",
        remoteUserId
    );


    return video;

}}


/*
============================================================
REMOVE REMOTE VIDEO
============================================================
*/

function removeRemoteVideo(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    const box =
        document.getElementById(
            "video-box-" + remoteUserId
        );


    if (box) {{

        box.remove();

        console.log(
            "REMOTE VIDEO REMOVED:",
            remoteUserId
        );

    }}

}}


/*
============================================================
CREATE PEER CONNECTION
============================================================
*/

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
        "===================================="
    );

    console.log(
        "CREATING PEER CONNECTION"
    );

    console.log(
        USER_ID,
        "<->",
        remoteUserId
    );

    console.log(
        "LOCAL STREAM READY:",
        !!localStream
    );

    console.log(
        "LOCAL TRACK COUNT:",
        localStream
            ? localStream.getTracks().length
            : 0
    );

    console.log(
        "===================================="
    );


    /*
    Browser-side STUN.
    No TURN required for this configuration.
    */

    const configuration = {{

        iceServers: [

            {{

                urls:
                    "stun:stun.l.google.com:19302"

            }}

        ]

    }};


    const pc =
        new RTCPeerConnection(
            configuration
        );


    peerConnections[
        remoteUserId
    ] = pc;


    iceQueues[
        remoteUserId
    ] = [];


    remoteStreams[
        remoteUserId
    ] = new MediaStream();


    const remoteVideo =
        createRemoteVideo(
            remoteUserId
        );


    /*
    ========================================================
    ADD LOCAL TRACKS
    ========================================================
    */

    if (!localStream) {{

        console.error(
            "CRITICAL: LOCAL STREAM NOT READY"
        );

    }}
    else {{

        localStream
            .getTracks()
            .forEach(
                function(track) {{

                    console.log(
                        "ADDING LOCAL TRACK:",
                        USER_ID,
                        track.kind,
                        "->",
                        remoteUserId
                    );


                    pc.addTrack(
                        track,
                        localStream
                    );

                }}
            );

    }}


    /*
    ========================================================
    REMOTE TRACK
    ========================================================
    */

    pc.ontrack =
        function(event) {{

            console.log(
                "===================================="
            );

            console.log(
                "REMOTE TRACK RECEIVED"
            );

            console.log(
                "LOCAL:",
                USER_ID
            );

            console.log(
                "REMOTE:",
                remoteUserId
            );

            console.log(
                "TRACK:",
                event.track.kind
            );

            console.log(
                "STREAMS:",
                event.streams
            );

            console.log(
                "===================================="
            );


            if (!remoteVideo) {{

                console.error(
                    "REMOTE VIDEO NOT FOUND:",
                    remoteUserId
                );

                return;

            }}


            if (
                event.streams &&
                event.streams.length > 0
            ) {{

                remoteVideo.srcObject =
                    event.streams[0];

            }}
            else {{

                remoteStreams[
                    remoteUserId
                ].addTrack(
                    event.track
                );


                remoteVideo.srcObject =
                    remoteStreams[
                        remoteUserId
                    ];

            }}


            remoteVideo
                .play()
                .then(
                    function() {{

                        console.log(
                            "REMOTE VIDEO PLAYING:",
                            remoteUserId
                        );

                    }}
                )
                .catch(
                    function(error) {{

                        console.warn(
                            "REMOTE PLAY ERROR:",
                            error
                        );

                    }}
                );

        }};


    /*
    ========================================================
    ICE CANDIDATE
    ========================================================
    */

    pc.onicecandidate =
        function(event) {{

            if (!event.candidate) {{

                console.log(
                    "ICE GATHERING COMPLETE:",
                    USER_ID,
                    "->",
                    remoteUserId
                );

                return;

            }}


            console.log(
                "LOCAL ICE:",
                USER_ID,
                "->",
                remoteUserId,
                event.candidate.candidate
            );


            if (
                !socket ||
                socket.readyState !==
                    WebSocket.OPEN
            ) {{

                console.warn(
                    "WEBSOCKET NOT OPEN - ICE NOT SENT"
                );

                return;

            }}


            const message = {{

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

            }};


            console.log(
                "SENDING ICE:",
                message
            );


            socket.send(
                JSON.stringify(
                    message
                )
            );

        }};


    /*
    ========================================================
    ICE GATHERING STATE
    ========================================================
    */

    pc.onicegatheringstatechange =
        function() {{

            console.log(
                "ICE GATHERING STATE:",
                remoteUserId,
                pc.iceGatheringState
            );

        }};


    /*
    ========================================================
    ICE CONNECTION STATE
    ========================================================
    */

    pc.oniceconnectionstatechange =
        function() {{

            console.log(
                "ICE CONNECTION STATE:",
                USER_ID,
                "<->",
                remoteUserId,
                pc.iceConnectionState
            );


            if (
                pc.iceConnectionState ===
                "checking"
            ) {{

                setStatus(
                    "Checking connection with " +
                    remoteUserId
                );

            }}


            if (
                pc.iceConnectionState ===
                "connected"
            ) {{

                console.log(
                    "===================================="
                );

                console.log(
                    "ICE CONNECTED"
                );

                console.log(
                    USER_ID,
                    "<->",
                    remoteUserId
                );

                console.log(
                    "===================================="
                );


                setStatus(
                    "Call connected with " +
                    remoteUserId
                );

            }}


            if (
                pc.iceConnectionState ===
                "completed"
            ) {{

                console.log(
                    "ICE COMPLETED:",
                    remoteUserId
                );

            }}


            if (
                pc.iceConnectionState ===
                "failed"
            ) {{

                console.error(
                    "===================================="
                );

                console.error(
                    "ICE CONNECTION FAILED"
                );

                console.error(
                    USER_ID,
                    "<->",
                    remoteUserId
                );

                console.error(
                    "===================================="
                );


                setStatus(
                    "ICE connection failed"
                );

            }}

        }};


    /*
    ========================================================
    PEER CONNECTION STATE
    ========================================================
    */

    pc.onconnectionstatechange =
        function() {{

            console.log(
                "PEER CONNECTION STATE:",
                USER_ID,
                "<->",
                remoteUserId,
                pc.connectionState
            );


            if (
                pc.connectionState ===
                "connected"
            ) {{

                setStatus(
                    "WebRTC connected with " +
                    remoteUserId
                );

            }}


            if (
                pc.connectionState ===
                "failed"
            ) {{

                setStatus(
                    "WebRTC connection failed"
                );

            }}

        }};


    /*
    ========================================================
    SIGNALING STATE
    ========================================================
    */

    pc.onsignalingstatechange =
        function() {{

            console.log(
                "SIGNALING STATE:",
                remoteUserId,
                pc.signalingState
            );

        }};


    /*
    ========================================================
    ICE CANDIDATE ERROR
    ========================================================
    */

    pc.onicecandidateerror =
        function(event) {{

            console.error(
                "ICE CANDIDATE ERROR:",
                remoteUserId,
                event
            );

        }};


    return pc;

}}


/*
============================================================
CREATE OFFER
============================================================
*/

async function createOffer(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    /*
    IMPORTANT:
    Never create an offer until local media exists.
    */

    const mediaReady =
        await mediaReadyPromise;


    if (!mediaReady) {{

        console.error(
            "MEDIA NOT READY - OFFER CANCELLED:",
            remoteUserId
        );

        return;

    }}


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
            "PEER ALREADY EXISTS:",
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
            "WEBSOCKET NOT OPEN"
        );

        return;

    }}


    if (makingOffer[remoteUserId]) {{

        return;

    }}


    makingOffer[remoteUserId] =
        true;


    const pc =
        createPeerConnection(
            remoteUserId
        );


    try {{

        console.log(
            "CREATING OFFER:",
            USER_ID,
            "->",
            remoteUserId
        );


        console.log(
            "TRACKS BEFORE OFFER:",
            pc.getSenders().map(
                function(sender) {{
                    return sender.track
                        ? sender.track.kind
                        : "NO TRACK";
                }}
            )
        );


        const offer =
            await pc.createOffer();


        await pc.setLocalDescription(
            offer
        );


        console.log(
            "LOCAL DESCRIPTION SET:",
            remoteUserId
        );


        console.log(
            "OFFER SDP:",
            pc.localDescription.sdp
        );


        const message = {{

            event:
                "offer",

            target:
                remoteUserId,

            sdp:
                pc.localDescription.sdp

        }};


        console.log(
            "SENDING OFFER:",
            message
        );


        socket.send(
            JSON.stringify(
                message
            )
        );


        console.log(
            "OFFER SENT:",
            USER_ID,
            "->",
            remoteUserId
        );


        setStatus(
            "Calling " +
            remoteUserId
        );

    }}
    catch(error) {{

        console.error(
            "CREATE OFFER ERROR:",
            error
        );

    }}
    finally {{

        makingOffer[
            remoteUserId
        ] = false;

    }}

}}


/*
============================================================
HANDLE OFFER
============================================================
*/

async function handleOffer(message) {{

    /*
    IMPORTANT:
    Incoming offer also waits for local media.
    */

    const mediaReady =
        await mediaReadyPromise;


    if (!mediaReady) {{

        console.error(
            "MEDIA NOT READY - OFFER IGNORED"
        );

        return;

    }}


    const remoteUserId =
        String(message.from);


    console.log(
        "===================================="
    );

    console.log(
        "OFFER RECEIVED:",
        remoteUserId,
        "->",
        USER_ID
    );

    console.log(
        "===================================="
    );


    const pc =
        createPeerConnection(
            remoteUserId
        );


    try {{

        await pc.setRemoteDescription(
            new RTCSessionDescription({{

                type:
                    "offer",

                sdp:
                    message.sdp

            }})
        );


        console.log(
            "REMOTE OFFER APPLIED:",
            remoteUserId
        );


        await flushIceQueue(
            remoteUserId
        );


        const answer =
            await pc.createAnswer();


        await pc.setLocalDescription(
            answer
        );


        const answerMessage = {{

            event:
                "answer",

            to:
                remoteUserId,

            sdp:
                pc.localDescription.sdp

        }};


        console.log(
            "SENDING ANSWER:",
            answerMessage
        );


        socket.send(
            JSON.stringify(
                answerMessage
            )
        );


        console.log(
            "ANSWER SENT:",
            USER_ID,
            "->",
            remoteUserId
        );


        setStatus(
            "Answer sent to " +
            remoteUserId
        );

    }}
    catch(error) {{

        console.error(
            "HANDLE OFFER ERROR:",
            error
        );

    }}

}}


/*
============================================================
HANDLE ANSWER
============================================================
*/

async function handleAnswer(message) {{

    const remoteUserId =
        String(message.from);


    console.log(
        "===================================="
    );

    console.log(
        "ANSWER RECEIVED:",
        remoteUserId,
        "->",
        USER_ID
    );

    console.log(
        "===================================="
    );


    const pc =
        peerConnections[
            remoteUserId
        ];


    if (!pc) {{

        console.error(
            "NO PEER FOR ANSWER:",
            remoteUserId
        );

        return;

    }}


    try {{

        await pc.setRemoteDescription(
            new RTCSessionDescription({{

                type:
                    "answer",

                sdp:
                    message.sdp

            }})
        );


        console.log(
            "REMOTE ANSWER APPLIED:",
            remoteUserId
        );


        await flushIceQueue(
            remoteUserId
        );


        console.log(
            "SENDERS AFTER ANSWER:",
            pc.getSenders().map(
                function(sender) {{
                    return sender.track
                        ? sender.track.kind
                        : "NO TRACK";
                }}
            )
        );


        setStatus(
            "Waiting for WebRTC connection..."
        );

    }}
    catch(error) {{

        console.error(
            "HANDLE ANSWER ERROR:",
            error
        );

    }}

}}


/*
============================================================
HANDLE ICE
============================================================
*/

async function handleIceCandidate(message) {{

    const remoteUserId =
        String(message.from);


    console.log(
        "REMOTE ICE RECEIVED:",
        remoteUserId,
        "->",
        USER_ID
    );


    if (!message.candidate) {{

        console.warn(
            "ICE MESSAGE WITHOUT CANDIDATE:",
            message
        );

        return;

    }}


    /*
    If an ICE message arrives before media,
    wait for media first.
    */

    await mediaReadyPromise;


    const pc =
        createPeerConnection(
            remoteUserId
        );


    const candidate =
        new RTCIceCandidate({{

            candidate:
                message.candidate,

            sdpMid:
                message.sdpMid,

            sdpMLineIndex:
                message.sdpMLineIndex

        }});


    if (!pc.remoteDescription) {{

        console.log(
            "QUEUEING ICE:",
            remoteUserId
        );


        iceQueues[
            remoteUserId
        ].push(candidate);


        return;

    }}


    try {{

        await pc.addIceCandidate(
            candidate
        );


        console.log(
            "ICE CANDIDATE ADDED:",
            remoteUserId
        );

    }}
    catch(error) {{

        console.error(
            "ADD ICE ERROR:",
            remoteUserId,
            error
        );

    }}

}}


/*
============================================================
FLUSH ICE QUEUE
============================================================
*/

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


    console.log(
        "FLUSHING ICE QUEUE:",
        remoteUserId,
        queue.length
    );


    while (
        queue.length > 0
    ) {{

        const candidate =
            queue.shift();


        try {{

            await pc.addIceCandidate(
                candidate
            );


            console.log(
                "QUEUED ICE ADDED:",
                remoteUserId
            );

        }}
        catch(error) {{

            console.error(
                "QUEUED ICE ERROR:",
                remoteUserId,
                error
            );

        }}

    }}

}}


/*
============================================================
CLOSE PEER
============================================================
*/

function closePeer(remoteUserId) {{

    remoteUserId =
        String(remoteUserId);


    const pc =
        peerConnections[
            remoteUserId
        ];


    if (pc) {{

        console.log(
            "CLOSING PEER:",
            remoteUserId
        );


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


    delete makingOffer[
        remoteUserId
    ];


    removeRemoteVideo(
        remoteUserId
    );

}}


/*
============================================================
START MEDIA
============================================================
*/

async function startMedia() {{

    try {{

        console.log(
            "===================================="
        );

        console.log(
            "REQUESTING CAMERA/MICROPHONE..."
        );

        console.log(
            "===================================="
        );


        localStream =
            await navigator
                .mediaDevices
                .getUserMedia({{

                    audio: true,

                    video: true

                }});


        console.log(
            "LOCAL MEDIA OBJECT CREATED"
        );


        const audioTracks =
            localStream.getAudioTracks();


        const videoTracks =
            localStream.getVideoTracks();


        console.log(
            "AUDIO TRACKS:",
            audioTracks.length
        );


        console.log(
            "VIDEO TRACKS:",
            videoTracks.length
        );


        audioTracks.forEach(
            function(track) {{

                console.log(
                    "AUDIO TRACK:",
                    track.id,
                    track.readyState,
                    track.enabled
                );

            }}
        );


        videoTracks.forEach(
            function(track) {{

                console.log(
                    "VIDEO TRACK:",
                    track.id,
                    track.readyState,
                    track.enabled
                );

            }}
        );


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
                        "LOCAL VIDEO PLAY ERROR:",
                        error
                    );

                }}
            );


        console.log(
            "LOCAL MEDIA STARTED"
        );


        setStatus(
            "Camera and microphone ready"
        );


        return true;

    }}
    catch(error) {{

        console.error(
            "GET USER MEDIA ERROR:",
            error
        );


        setStatus(
            "Camera/microphone permission denied"
        );


        return false;

    }}

}}


/*
============================================================
WEBSOCKET
============================================================
*/

function connectWebSocket() {{

    console.log(
        "CONNECTING WEBSOCKET:",
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
                "WEBSOCKET CONNECTED:",
                USER_ID
            );


            setStatus(
                "Signaling connected"
            );


            /*
            IMPORTANT:

            Start media BEFORE requesting users.
            */

            mediaReadyPromise =
                startMedia();


            const mediaStarted =
                await mediaReadyPromise;


            if (!mediaStarted) {{

                console.error(
                    "MEDIA START FAILED"
                );

                return;

            }}


            console.log(
                "===================================="
            );

            console.log(
                "MEDIA READY BEFORE SIGNALING"
            );

            console.log(
                "USER:",
                USER_ID
            );

            console.log(
                "TRACKS:",
                localStream.getTracks().length
            );

            console.log(
                "===================================="
            );


            console.log(
                "REQUESTING EXISTING USERS"
            );


            /*
            Backend may already have sent its automatic
            existing_users message.

            This request is safe because createOffer()
            checks whether a peer already exists.
            */

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
                    "WS MESSAGE:",
                    message
                );


                /*
                ============================================
                EXISTING USERS
                ============================================
                */

                if (
                    message.event ===
                    "existing_users"
                ) {{

                    /*
                    CRITICAL FIX:

                    Wait for camera/microphone before creating
                    any RTCPeerConnection or offer.
                    */

                    const mediaStarted =
                        await mediaReadyPromise;


                    if (!mediaStarted) {{

                        console.error(
                            "MEDIA NOT READY - EXISTING USERS IGNORED"
                        );

                        return;

                    }}


                    const users =
                        message.users || [];


                    console.log(
                        "EXISTING USERS:",
                        users
                    );


                    /*
                    Newly connected user creates offers.
                    */

                    for (
                        const remoteUserId
                        of users
                    ) {{

                        if (
                            String(remoteUserId) !==
                            String(USER_ID)
                        ) {{

                            await createOffer(
                                remoteUserId
                            );

                        }}

                    }}


                    return;

                }}


                /*
                ============================================
                USER JOINED
                ============================================
                */

                if (
                    message.event ===
                    "user_joined"
                ) {{

                    const remoteUserId =
                        String(
                            message.user_id
                        );


                    console.log(
                        "USER JOINED:",
                        remoteUserId
                    );


                    /*
                    Do NOT create an offer here.

                    The newly joined browser receives
                    existing_users and creates the offer.
                    */

                    return;

                }}


                /*
                ============================================
                OFFER
                ============================================
                */

                if (
                    message.event ===
                    "offer"
                ) {{

                    await handleOffer(
                        message
                    );

                    return;

                }}


                /*
                ============================================
                ANSWER
                ============================================
                */

                if (
                    message.event ===
                    "answer"
                ) {{

                    await handleAnswer(
                        message
                    );

                    return;

                }}


                /*
                ============================================
                ICE
                ============================================
                */

                if (
                    message.event ===
                    "ice_candidate"
                ) {{

                    await handleIceCandidate(
                        message
                    );

                    return;

                }}


                /*
                ============================================
                USER LEFT
                ============================================
                */

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

            }}
            catch(error) {{

                console.error(
                    "WEBSOCKET MESSAGE ERROR:",
                    error
                );

            }}

        }};


    socket.onerror =
        function(error) {{

            console.error(
                "WEBSOCKET ERROR:",
                error
            );


            setStatus(
                "WebSocket error"
            );

        }};


    socket.onclose =
        function(event) {{

            console.log(
                "WEBSOCKET CLOSED:",
                event.code,
                event.reason
            );


            setStatus(
                "Disconnected"
            );

        }};

}}


/*
============================================================
MUTE
============================================================
*/

function toggleMute() {{

    if (!localStream) {{

        return;

    }}


    const tracks =
        localStream.getAudioTracks();


    tracks.forEach(
        function(track) {{

            track.enabled =
                !track.enabled;

        }}
    );


    const muted =
        tracks.length > 0
            ? !tracks[0].enabled
            : false;


    console.log(
        "MIC MUTED:",
        muted
    );


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


/*
============================================================
CAMERA
============================================================
*/

function toggleCamera() {{

    if (!localStream) {{

        return;

    }}


    const tracks =
        localStream.getVideoTracks();


    tracks.forEach(
        function(track) {{

            track.enabled =
                !track.enabled;

        }}
    );


    const enabled =
        tracks.length > 0
            ? tracks[0].enabled
            : false;


    console.log(
        "CAMERA ENABLED:",
        enabled
    );


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


/*
============================================================
START
============================================================
*/

connectWebSocket();

</script>

</body>

</html>
"""


    # ========================================================
    # RENDER WEBRTC
    # ========================================================

    components.html(
        html_code,
        height=720,
        scrolling=False,
    )


# ============================================================
# END CALL BUTTON
# ============================================================

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
