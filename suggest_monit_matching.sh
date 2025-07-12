#!/bin/bash

echo "🔎 Analizando procesos actuales de gunicorn y celery..."

# Buscar procesos gunicorn
echo -e "\n🎯 Gunicorn:"
ps aux | grep gunicorn | grep -v grep | while read -r line ; do
    echo "-------------------------------------------"
    echo "$line"
    match=$(echo "$line" | grep -oP "(?<=-c )[^ ]+")
    app=$(echo "$line" | grep -oP "(?<= )[^ ]+:[^ ]+")
    if [[ ! -z "$match" && ! -z "$app" ]]; then
        echo "👉 Sugerencia para Monit matching: \"${match}\""
    else
        echo "⚠️ No se pudo extraer el matching automáticamente, revisar manualmente."
    fi
done

# Buscar procesos celery
echo -e "\n🎯 Celery:"
ps aux | grep celery | grep -v grep | while read -r line ; do
    echo "-------------------------------------------"
    echo "$line"
    match=$(echo "$line" | grep -oP "celery.*worker")
    if [[ ! -z "$match" ]]; then
        echo "👉 Sugerencia para Monit matching: \"$match\""
    else
        echo "⚠️ No se pudo extraer el matching automáticamente, revisar manualmente."
    fi
done

echo -e "\n✅ Listo. Basado en esto podés actualizar tus archivos en /etc/monit/conf-enabled/"
