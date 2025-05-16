from PIL import Image
from laplacianPipelined import LaplacianPipelined
from gaussianPipelined import GaussianPipelined 
from pymtl3 import *
def load_png(filename):
    """Carga una imagen BMP en escala de grises."""
    image = Image.open(filename).convert("L")  # Convertir a escala de grises
    width, height = image.size
    pixels = list(image.getdata())  # Obtener los píxeles como lista
    image_matrix = [pixels[i * width:(i + 1) * width] for i in range(height)]
    return image_matrix, width, height

def save_png(filename, image, width, height):
    """Guarda una imagen en formato BMP."""
    output_image = Image.new("L", (width, height))  # Crear imagen en escala de grises
    pixels = [pixel for row in image for pixel in row]  # Convertir matriz a lista
    output_image.putdata(pixels)
    output_image.save(filename)

def apply_filter(image, width, height, kernel, divisor=1):
    """Aplica un filtro de convolución a la imagen."""
    offset = len(kernel) // 2  # Calcula el desplazamiento según el tamaño del kernel
    new_image = [[0] * width for _ in range(height)]  # Crea una nueva imagen vacía

    # Recorre la imagen ignorando los bordes
    for y in range(offset, height - offset):  
        for x in range(offset, width - offset):  
            pixel_value = 0  # Inicializa el valor del píxel filtrado

            # Aplica la convolución con el kernel
            for j in range(len(kernel)):  
                for i in range(len(kernel[j])):  
                    pixel_value += kernel[j][i] * image[y + j - offset][x + i - offset] 

            # Normalización y recorte de valores
            pixel_value //= divisor  # Aplicar el divisor
            if pixel_value < 0:
                pixel_value = 0
            elif pixel_value > 255:
                pixel_value = 255
            new_image[y][x] = pixel_value

    return new_image

def gaussian_filter(image, width, height):
    """Filtro Gaussiano 5x5."""
    kernel = [[1,  2,  1],
          [2,  4,  2],
          [1,  2,  1]]
    return apply_filter(image, width, height, kernel, divisor=16)

def laplacian_filter(image, width, height):
    """Filtro Laplaciano 5x5."""
    kernel = [[ 0,  1,  0],
            [ 1, -4,  1],
            [ 0,  1,  0]]
    return apply_filter(image, width, height, kernel)

def edge_detection(image, width, height):
    """Aplica detección de bordes con Gaussiano y Laplaciano."""
    #edges = gaussian_filter(image, width, height)
    edges = laplacian_filter(image, width, height)
    return edges

def gaussianPipelinePyMTL(image, width, height):
    
    edges = [[0 for _ in range(width)] for _ in range(height)]
    dut = GaussianPipelined(x_size=width, y_size=height)
    dut.apply(DefaultPassGroup(linetrace=False))
    dut.sim_reset()
    for row in range(height):
        for col in range(width):
            pixel = image[row][col]
            dut.pixel_in @= pixel
            dut.sim_tick()
            if dut.valid_out == 1:
                r_idx = dut.reg_row_idx.uint() -1
                c_idx = dut.reg_col_idx.uint()

                if 0 <= r_idx < height and 0 <= c_idx < width:
                    edges[r_idx][c_idx] = dut.pixel_out.uint()
    return edges

def laplacianPipelinePyMTL(image, width, height):

    edges = [[0 for _ in range(width)] for _ in range(height)]
    dut = LaplacianPipelined(x_size=width, y_size=height)
    dut.apply(DefaultPassGroup(linetrace=False))
    dut.sim_reset()
    for row in range(height):
        for col in range(width):
            pixel = image[row][col]
            dut.pixel_in @= pixel
            dut.sim_tick()
            if dut.valid_out == 1:
                r_idx = dut.reg_row_idx.uint() -1
                c_idx = dut.reg_col_idx.uint()

                if 0 <= r_idx < height and 0 <= c_idx < width:
                    edges[r_idx][c_idx] = dut.pixel_out.uint()

    return edges
def main(input_file, output_file):
    image, width, height = load_png(input_file)
    #processed_image = gaussianPipelinePyMTL(image, width, height)
    processed_image = edge_detection(image, width, height)
    save_png(output_file, processed_image, width, height)
    print(f"Imagen procesada guardada en {output_file}. Height es {height} y su width es {width}")

if __name__ == "__main__":
    main("cameraman.bmp", "Cameraman_Laplacian_SW.bmp")
