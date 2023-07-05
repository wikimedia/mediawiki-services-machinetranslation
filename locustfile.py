import random

from locust import HttpUser, between, task

languages = ["ig", "ml", "bn", "es", "mr", "hi", "fi", "he"]


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    @task(1)
    def index(self):
        self.client.get("/")

    @task(2)
    def translate(self):
        text = """
Jazz is a music genre that originated in the African-American communities \
of New Orleans, Louisiana, United States, in the late 19th and early 20th \
centuries, with its roots in blues and ragtime.
Since the 1920s Jazz Age, it has been recognized as a major form of musical \
expression in traditional and popular music, linked by the common bonds of \
African-American and European-American musical parentage.
Jazz is characterized by swing and blue notes, complex chords, call and \
response vocals, polyrhythms and improvisation.
Jazz has roots in West African cultural and musical expression, and in \
African-American music traditions.
      """
        src = "en"
        tgt = random.choice(languages)
        self.client.post(f"/api/translate/{src}/{tgt}", json={"text": text})
