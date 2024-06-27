import pandas as pd

from sklearn.model_selection import train_test_split
from challenge.model import DelayModel

model = DelayModel()
data = pd.read_csv(filepath_or_buffer="data/data.csv")

features, target = model.preprocess(
    data=data,
    target_column="delay"
)

_, features_validation, _, target_validation = train_test_split(features, target, test_size = 0.33, random_state = 42)

model.fit(
    features=features,
    target=target
)
