#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPAsyncWebServer.h>

// Configuración de la red Wi-Fi
const char* ssid = "MELVALUCAS";
const char* password = "Contraseña";

// Dirección base de la API
const char* baseUrl = "https://parcialanaliticadedatos251-1.onrender.com/";

// Crear una instancia de servidor HTTP asincrónico
AsyncWebServer server(80);

// Variable para almacenar el nombre de usuario
String usuario = "elonmusk";  // Nombre de usuario por defecto

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Conectar a la red Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConexión WiFi establecida");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Configurar la ruta POST para recibir el nombre de usuario
  server.on("/set_usuario", HTTP_POST, [](AsyncWebServerRequest *request){
    if (request->hasParam("usuario", true)) {
      usuario = request->getParam("usuario", true)->value();  // Obtener el nombre de usuario
      Serial.print("Nombre de usuario cambiado a: ");
      Serial.println(usuario);
      request->send(200, "text/plain", "Nombre de usuario actualizado");
    } else {
      request->send(400, "text/plain", "Falta el parámetro usuario");
    }
  });

  // Iniciar el servidor
  server.begin();
}

void loop() {
  // Construir la URL dinámica con el nombre de usuario
  String url = baseUrl + usuario;

  // Realizar la solicitud HTTP cada 10 segundos
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);
    int httpCode = http.GET();

    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println("Respuesta del servidor:");
      Serial.println(payload);
    } else {
      Serial.printf("Error en la solicitud HTTP: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  } else {
    Serial.println("No se pudo conectar a la red Wi-Fi");
  }

  delay(10000);  // Espera 10 segundos antes de la siguiente solicitud
}