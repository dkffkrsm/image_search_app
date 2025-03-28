import numpy as np
import cv2
from sklearn.random_projection import SparseRandomProjection
from PIL import Image

class RandomProjectionHasher:
    def __init__(self, n_bits=32):
        self.n_bits = n_bits
        self.hasher = SparseRandomProjection(n_components=n_bits)

    def fit(self, descriptors):
        self.hasher.fit(descriptors)

    def hash(self, descriptors):
        projections = self.hasher.transform(descriptors)
        return ["".join(['1' if val > 0 else '0' for val in row]) for row in projections]

def get_image_hashes(image: Image.Image) -> list[str]:
    """
    이미지에서 SIFT 특징점을 추출하고,
    Random Projection을 통해 32비트 해시 리스트 생성.
    """
    gray = np.array(image.convert("L"))
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)

    if descriptors is None or len(descriptors) == 0:
        return []

    hasher = RandomProjectionHasher(n_bits=32)
    hasher.fit(descriptors)
    return hasher.hash(descriptors)
