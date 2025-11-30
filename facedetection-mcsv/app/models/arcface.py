# Archivo: arcface.py
import torch.nn as nn
import torch.nn.functional as F

from .iresnet import iresnet50

class Arcface(nn.Module):
    def __init__(self, backbone='iresnet50', mode='predict'):
        """
        Wrapper del modelo Arcface simplificado para inferencia.
        """
        super(Arcface, self).__init__()
        
        if backbone == 'iresnet50':
            embedding_size = 512
            # Construimos nuestro backbone iresnet50
            self.arcface = iresnet50(dropout_keep_prob=0.5, embedding_size=embedding_size)
        else:
            raise ValueError(f"Este wrapper simplificado solo soporta 'iresnet50', pero se pidió '{backbone}'")

        if mode != 'predict':
            raise ValueError("Este wrapper simplificado solo soporta el modo 'predict'.")
        self.mode = mode

    def forward(self, x):
        """
        Pasa la entrada a través del backbone y devuelve el embedding normalizado.
        """
        # 1. Obtener las características del backbone
        x = self.arcface(x)
        # 2. Asegurarse de que la salida es un vector plano
        x = x.view(x.size()[0], -1)
        # 3. Normalizar el vector de características (embedding)
        x = F.normalize(x)
        return x
