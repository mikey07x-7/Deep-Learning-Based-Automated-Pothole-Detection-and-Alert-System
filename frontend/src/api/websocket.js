// websocket client wrapper
export function createWebsocket(url, onMessage) {
  const ws = new WebSocket(url);
  ws.onopen = () => console.log("ws open");
  ws.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data);
      onMessage(data);
    } catch (err) {
      console.log("ws msg", evt.data);
    }
  };
  ws.onclose = () => console.log("ws closed");
  ws.onerror = () => console.log("ws error");
  return ws;
}
