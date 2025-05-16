import cv2
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

# Cargar imágenes (grises o RGB)
img1 = cv2.imread('cameraman_laplacianPyMTL.bmp', cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread('cameraman_laplacian_SW.bmp', cv2.IMREAD_GRAYSCALE)
img3 = cv2.imread('cameraman_gaussianPyMTL.bmp', cv2.IMREAD_GRAYSCALE)
img4 = cv2.imread('cameraman_gaussian_SW.bmp', cv2.IMREAD_GRAYSCALE)
# Calcular PSNR
psnr_val = psnr(img1, img2)
print(f'PSNR: {psnr_val:.2f} dB')
psnr_val = psnr(img4, img3)
print(f'PSNR: {psnr_val:.2f} dB')
# Calcular SSIM
ssim_val = ssim(img1, img2)
print(f'SSIM: {ssim_val:.4f}')
ssim_val = ssim(img4, img3)
print(f'SSIM: {ssim_val:.4f}')
