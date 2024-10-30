# Используем официальный образ Python в качестве базового образа
FROM python:3.11
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /usr/src/app
# Копируем файл req.txt внутрь контейнера
COPY req.txt ./
# Устанавливаем зависимости, описанные в файле req.txt
RUN pip install -r req.txt