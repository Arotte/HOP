import gensim.downloader as api

MODEL_TO_DOWNLOAD = "glove-twitter-25"

model_path = api.load(
    MODEL_TO_DOWNLOAD,
    return_path=True,
)

print(model_path)
