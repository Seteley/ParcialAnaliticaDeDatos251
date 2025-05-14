#include <WiFi.h>
#include <HTTPClient.h>

// Configuración de la red Wi-Fi
const char* ssid = "MELVALUCAS";           // Nombre de la red Wi-Fi
const char* password = "Contraseña";       // Contraseña de la red Wi-Fi

// Dirección base de la API o servidor
const char* baseUrl = "https://parcialanaliticadedatos251-1.onrender.com/";

// Nombre de usuario por defecto
String usuario = "elonmusk";  // Nombre de usuario inicial

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
  Serial.println("Esperando nombre de usuario desde Python...");
}

void loop() {
  // Verificar si hay datos disponibles desde el puerto serial
  if (Serial.available() > 0) {
    usuario = Serial.readString();  // Leer el nombre de usuario enviado desde Python
    usuario.trim();  // Eliminar espacios extra

    Serial.print("Nombre de usuario recibido: ");
    Serial.println(usuario);  // Mostrar el nombre de usuario recibido
  }

  // Construir la URL dinámica con el nombre de usuario
  String url = baseUrl + usuario;  // Ejemplo: "https://parcialanaliticadedatos251-1.onrender.com/monitoreo/elonmusk"

  // Realizar la solicitud HTTP cada 10 segundos
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Especifica la URL completa del servidor con el nombre de usuario
    http.begin(url);

    // Realiza la solicitud GET
    int httpCode = http.GET();

    // Si la solicitud fue exitosa, imprime los resultados
    if (httpCode > 0) {
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