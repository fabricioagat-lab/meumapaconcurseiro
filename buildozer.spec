[app]
title = Meu Mapa Concurseiro
package.name = meumapaconcurseiro
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 0.1
requirements = python3,kivy==2.2.1,plyer,reportlab
orientation = portrait
android.arch = arm64-v8a

# (android)
android.api = 33
android.minapi = 21
android.sdk = 24

# permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# Se você NÃO for subir um ícone agora, APAGUE a linha abaixo:
# icon.filename = assets/icon.png
