#include <WiFi.h>
#include <HTTPClient.h>

// Configuración de la red Wi-Fi
const char* ssid = "MELVALUCAS";           // Nombre de la red Wi-Fi
const char* password = "Contraseña";  // Contraseña de la red Wi-Fi

// Dirección de la API o servidor al que quieres hacer la solicitud
const char* serverUrl = "https://parcialanaliticadedatos251-1.onrender.com/monitoreo/nombre_usuario";

void setup() {
  // Iniciar el monitor serial
  Serial.begin(115200);
  delay(1000);

  // Conectar a la red Wi-Fi
  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  // Esperar hasta que esté conectado
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConexión WiFi establecida");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());  // Imprime la dirección IP asignada
}

void loop() {
  // Realizar la solicitud HTTP cada 10 segundos
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Especifica la URL del servidor
    http.begin(serverUrl); 

    // Realiza la solicitud GET
    int httpCode = http.GET();

    // Si la solicitud fue exitosa, imprime los resultados
    if (httpCode > 0) {
      Serial.printf("Código de respuesta: %d\n", httpCode);
      String payload = http.getString();
      Serial.println("Respuesta del servidor:");
      Serial.println(payload);
    } else {
      // En caso de error en la solicitud
      Serial.printf("Error en la solicitud HTTP: %s\n", http.errorToString(httpCode).c_str());
    }

    // Cierra la conexión HTTP
    http.end();
  } else {
    Serial.println("No se pudo conectar a la red Wi-Fi");
  }

  // Esperar 10 segundos antes de la siguiente ejecución
  delay(10000);  // 10000 ms = 10 segundos
}