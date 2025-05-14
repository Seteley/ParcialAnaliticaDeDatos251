#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>

// Wi-Fi
const char* ssid = "MELVALUCAS";
const char* password = "GMS162030";

// URL fija
const char* url = "https://parcialanaliticadedatos251-1.onrender.com/monitoreo/nombre_usuario";

// Servidor web en el puerto 80
WebServer server(80);

// Última respuesta recibida
String ultimaRespuesta = "{}";

// Temporizador
unsigned long ultimaConsulta = 0;
const unsigned long intervaloConsulta = 10000; // 10 segundos

// Manejador de la ruta /usuario
void handleGetUsuario() {
  server.send(200, "application/json", ultimaRespuesta);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Conexión WiFi
  //Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    //Serial.print(".");
  }

  //Serial.println("\n✅ WiFi conectado");
  //Serial.print("IP local: ");
  //Serial.println(WiFi.localIP());

  // Servidor HTTP
  server.on("/usuario", HTTP_GET, handleGetUsuario);
  server.begin();
}

void loop() {
  server.handleClient();

  // Ejecutar GET cada 10 segundos
  if (millis() - ultimaConsulta >= intervaloConsulta) {
    ultimaConsulta = millis();

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(url);

      int httpCode = http.GET();
      if (httpCode > 0) {
        ultimaRespuesta = http.getString();
        // Serial.println("📦 Respuesta recibida:");
        Serial.println(ultimaRespuesta);
      } else {
        ultimaRespuesta = "{\"error\":\"Fallo en solicitud\"}";
        Serial.printf("❌ Error HTTP: %s\n", http.errorToString(httpCode).c_str());
      }
      http.end();
    } else {
      Serial.println("❌ WiFi desconectado");
    }
  }
}
