/* eslint-disable no-undef */
importScripts('https://www.gstatic.com/firebasejs/12.6.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.6.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyBuZrl2zjPrpOFD_2pZKJTDe1AiRUArviA",
  authDomain: "bonusapp-1146e.firebaseapp.com",
  projectId: "bonusapp-1146e",
  storageBucket: "bonusapp-1146e.firebasestorage.app",
  messagingSenderId: "127439540218",
  appId: "1:127439540218:web:c504c60bc6db03c2181e43",
  measurementId: "G-3BF4XCB9VZ"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  const notification = payload.notification || {};
  const notificationTitle = notification.title || "Bonus";
  const notificationOptions = {
    body: notification.body || "You have a new message",
    icon: notification.icon || "/static/favicon.ico",
    data: {
      url: payload?.data?.url || "/",
      ...payload.data,
    },
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

self.addEventListener("notificationclick", function(event) {
  event.notification.close();
  const destination = event.notification?.data?.url || "/";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then(windowClients => {
      for (const client of windowClients) {
        if (client.url === destination && "focus" in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(destination);
      }
      return null;
    })
  );
});

