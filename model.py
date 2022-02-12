import pickle


class Model:
    def __init__(self):
        self.model = pickle.load(open('model_MLP.pkl', 'rb'))

    def __str__(self):
        return f"MLP regression model"

    def predict_result(self, inputs):
        return self.model.predict(inputs)