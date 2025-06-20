// ==UserScript==
// @name         Audio Latency Capturer VAPI
// @namespace    http://tampermonkey.net/
// @version      2025-05-13
// @description  audio capture streaming data over webRTC on websocket
// @author       nohren
// @match        https://dashboard.vapi.ai/assistants/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
  "use strict";

  //global script memory
  let st1, st2;
  let RTTHist = [],
    perceptionHist = [];

  //const CLIP_UPPER = 7000

  // create a global array to hold every peer‐connection
  //window._capturedPCs = [];

  // wrap the native constructor
  //const NativePC = window.RTCPeerConnection;
  //window.RTCPeerConnection = function (config, constraints) {
  //const pc = new NativePC(config, constraints);
  // window._capturedPCs.push(pc);
  // return pc;
  // };
  // preserve the prototype (so endless things don’t break)
  //window.RTCPeerConnection.prototype = NativePC.prototype;

  let gate1 = false,
    gate2 = false;

  let buttonPlaced = false;

  async function decodeMsg(msg) {
    //console.log(msg)
    //s.timestamp is a DOMHighResTimeStamp (double) storing the time value in milliseconds
    if (msg.msgStr === "sig-msg") {
      const serverTS = msg.serverTS;
      let data;
      try {
        data = JSON.parse(msg.msgData);
      } catch (e) {
        //console.log(e)
      }
      if (!data) return;

      //when user starts talking
      if (
        data.type === "speech-update" &&
        data.role === "user" &&
        data.status === "started"
      ) {
        if (!buttonPlaced) {
          const endCallBtn = document
            .querySelector("div.text-md.ml-1.font-medium")
            ?.closest("button");

          console.log(endCallBtn);

          if (endCallBtn) {
            function cleanup() {
              console.log("End Call clicked!");
              buttonPlaced = false;
              RTTHist = [];
              perceptionHist = [];
              endCallBtn.removeEventListener("click", cleanup);
            }
            buttonPlaced = true;
            // 2. wire up your listener
            endCallBtn.addEventListener("click", cleanup);
          }
        }
        console.log(`user started speaking`);
        gate1 = false;
        gate2 = false;
        //when user stops talking
      } else if (
        data.type === "speech-update" &&
        data.role === "user" &&
        data.status === "stopped"
      ) {
        //const st = await window._capturedPCs[1].getStats().then(res => {
        // return Array.from(res.values())
        //    .filter(s => s.type === "outbound-rtp")
        //   .reduce((acc, cv) => Math.max(acc, cv.timestamp), 0);
        //})
        console.log(`user stopped speaking`);
        st1 = serverTS;
        st2 = serverTS;
        gate1 = false;
        gate2 = false;

        //when assistant starts talking
      } else if (data.type === "transcript" && data.role === "assistant") {
        //console.log('model started speaking, get recv timestamp')
        if (!gate2) {
          gate2 = true;

          if (st2) {
            const diff = serverTS - st2;
            perceptionHist.push(diff);
            let mean = diff;
            if (perceptionHist.length > 1) {
              mean =
                perceptionHist.reduce((acc, cdiff) => acc + cdiff, 0) /
                perceptionHist.length;
            }

            console.log(`
                      assistant starts talking:

                      percieved latency: ${diff.toFixed(1)}ms

                      percieced mean latency: ${mean.toFixed(1)}ms
                      `);
            st2 = null;
          }
        }
      } else if (
        (data.type === "speech-update" && data.status === "started") ||
        data.type === "model-output"
      ) {
        if (!gate1) {
          gate1 = true;

          //let rt = await window._capturedPCs[2].getStats().then(res => {
          //   const inbound = Array.from(res.values())
          //  .filter(s => s.type === "inbound-rtp" && s.kind === "audio")
          //  return inbound.reduce((acc, cv) => Math.max(acc, cv.timestamp), 0)
          //})

          //calculate diff between send and recieve
          if (st1) {
            const diff = Math.min(serverTS - st1); // don't let random weird webRTC getStats hiccups from killing average
            RTTHist.push(diff);
            //average diff
            let mean = diff;
            if (RTTHist.length > 1) {
              mean =
                RTTHist.reduce((acc, cdiff) => acc + cdiff, 0) / RTTHist.length;
            }

            //Percieved - RTT latency = VAD delay
            console.log(`
                      RTT complete - payload recieved on client:

                      RTT latency: ${diff.toFixed(1)}ms

                      RTT mean latency: ${mean.toFixed(1)}ms

                      `);
            st1 = null;
          }
        }
      }
    }
  }

  const RealWS = WebSocket;
  window.WebSocket = function (url, protocols) {
    const ws = new RealWS(url, protocols);
    ws.addEventListener("message", (evt) => {
      let msg;
      try {
        msg = JSON.parse(evt.data);
      } catch (_) {
        return;
      }
      decodeMsg(msg);
    });
    return ws;
  };

  window.WebSocket.prototype = RealWS.prototype;
  window.WebSocket.OPEN = RealWS.OPEN;
  window.WebSocket.CLOSED = RealWS.CLOSED;
})();
