# How to set up the environment for G2SAT

## Alienware - Ubuntu 20.04 with RTX3090












## DGX Station - Ubuntu 18.04
1. Nvidia driver info - `nvidia-smi`: 
   `Driver Version`: 418.126.02   
   `CUDA Version`: 10.1

2. `nvcc -V`: 10.1

3. Install pytorch:
   `pip install torch==1.7.1+cu101 torchvision==0.8.2+cu101 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html`

4. Install pytorch-geometric
   `python -c "import torch; print(torch.__version__)"` -> 1.7.1+cu101
   CUDA version pytorch was installed with: `python -c "import torch; print(torch.version.cuda)"` -> 10.1
   
   ```python
    pip install torch-scatter -f https://pytorch-geometric.com/whl/torch-1.7.1+cu101.html
    pip install torch-sparse -f https://pytorch-geometric.com/whl/torch-1.7.1+cu101.html
    pip install torch-cluster -f https://pytorch-geometric.com/whl/torch-1.7.1+cu101.html
    pip install torch-spline-conv -f https://pytorch-geometric.com/whl/torch-1.7.1+cu101.html
    pip install torch-geometric
   ```


   