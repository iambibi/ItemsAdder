from PIL import Image
import os

def image_to_glsl_split(image_path, output_dir, compress=True):
    """
    Convertit une image en deux fichiers GLSL (gauche et droite)
    """
    # Ouvrir l'image
    img = Image.open(image_path)
    
    # Convertir en RGBA si nécessaire
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    width, height = img.size
    mid_width = width // 2
    
    # Dictionnaires pour organiser les pixels par couleur (gauche et droite)
    colors_dict_left = {}
    colors_dict_right = {}
    
    # Parcourir tous les pixels
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            
            # Ignorer les pixels transparents
            if a != 255:
                continue
            
            # Calculer l'index du pixel
            pixel_index = y * width + x
            
            # Organiser par couleur selon la position (gauche ou droite)
            color_key = (r, g, b)
            
            if x < mid_width:  # Partie gauche
                if color_key not in colors_dict_left:
                    colors_dict_left[color_key] = []
                colors_dict_left[color_key].append(pixel_index)
            else:  # Partie droite
                if color_key not in colors_dict_right:
                    colors_dict_right[color_key] = []
                colors_dict_right[color_key].append(pixel_index)
    
    # Créer les fichiers GLSL
    create_glsl_file(colors_dict_left, os.path.join(output_dir, "logo_openmc_left.glsl"), "Left", compress)
    create_glsl_file(colors_dict_right, os.path.join(output_dir, "logo_openmc_right.glsl"), "Right", compress)
    
    print(f"Fichiers GLSL générés dans : {output_dir}")
    print(f"Dimensions image : {width}x{height}")
    print(f"Point de séparation : x = {mid_width}")
    print(f"Mode compression : {'Activé' if compress else 'Désactivé'}")
    print(f"Couleurs différentes (gauche) : {len(colors_dict_left)}")
    print(f"Couleurs différentes (droite) : {len(colors_dict_right)}")
    print(f"Pixels gauche : {sum(len(indices) for indices in colors_dict_left.values())}")
    print(f"Pixels droite : {sum(len(indices) for indices in colors_dict_right.values())}")

def create_glsl_file(colors_dict, output_path, side, compress=True):
    """
    Crée un fichier GLSL pour un côté spécifique avec option de compression
    """
    # Vérifier si il y a des pixels
    if not colors_dict:
        print(f"Aucun pixel non-transparent trouvé pour le côté {side} !")
        content = f"vec3 pColor{side}(ivec2 RealPixelPos,ivec2 imageSize){{return vec3(-1);}}"
        with open(output_path, 'w') as f:
            f.write(content)
        return
    
    if compress:
        # Version compressée - tout sur une seule ligne
        glsl_parts = [f"vec3 pColor{side}(ivec2 RealPixelPos,ivec2 imageSize){{int pixelI=RealPixelPos.y*imageSize.x+RealPixelPos.x;switch(pixelI){{"]
        
        # Trier les couleurs par nombre d'occurrences (plus fréquentes d'abord)
        sorted_colors = sorted(colors_dict.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Générer les cases pour chaque couleur de manière compacte
        for (r, g, b), indices in sorted_colors:
            indices.sort()
            # Ajouter tous les cases d'une couleur ensemble
            cases = "".join(f"case {index}:" for index in indices)
            glsl_parts.append(f"{cases}return vec3({r},{g},{b});")
        
        # Ajouter le case par défaut
        glsl_parts.append("default:return vec3(-1);}}")
        
        # Joindre tout sans espaces
        glsl_content = "".join(glsl_parts)
        
    else:
        # Version lisible (comme avant)
        glsl_content = [
            f"vec3 pColor{side}(ivec2 RealPixelPos, ivec2 imageSize) {{",
            "    int pixelI = RealPixelPos.y * imageSize.x + RealPixelPos.x;",
            "    switch(pixelI) {"
        ]
        
        sorted_colors = sorted(colors_dict.items(), key=lambda x: len(x[1]), reverse=True)
        
        for (r, g, b), indices in sorted_colors:
            indices.sort()
            for index in indices:
                glsl_content.append(f"        case {index}:")
            glsl_content.append(f"            return vec3({r}, {g}, {b});")
        
        glsl_content.extend([
            "        default:",
            "            return vec3(-1);",
            "    }",
            "}"
        ])
        
        glsl_content = '\n'.join(glsl_content)
    
    # Écrire le fichier
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(glsl_content)
    
    # Afficher la taille du fichier
    file_size = len(glsl_content.encode('utf-8'))
    print(f"Fichier {side} généré : {file_size} bytes")

def create_glsl_file_ultra_compressed(colors_dict, output_path, side):
    """
    Version ultra-compressée avec regroupement de cases consécutives
    """
    if not colors_dict:
        with open(output_path, 'w') as f:
            f.write(f"vec3 pColor{side}(ivec2 p,ivec2 s){{return vec3(-1);}}")
        return
    
    # Construire le contenu ultra-compressé
    parts = [f"vec3 pColor{side}(ivec2 p,ivec2 s){{int i=p.y*s.x+p.x;switch(i){{"]
    
    sorted_colors = sorted(colors_dict.items(), key=lambda x: len(x[1]), reverse=True)
    
    for (r, g, b), indices in sorted_colors:
        indices.sort()
        # Regrouper les cases consécutives
        ranges = group_consecutive_ranges(indices)
        
        for start, end in ranges:
            if start == end:
                parts.append(f"case {start}:")
            else:
                # Pour les ranges, on doit quand même lister tous les cases
                for i in range(start, end + 1):
                    parts.append(f"case {i}:")
        
        parts.append(f"return vec3({r},{g},{b});")
    
    parts.append("default:return vec3(-1);}}")
    
    content = "".join(parts)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fichier {side} ultra-compressé : {len(content.encode('utf-8'))} bytes")

def group_consecutive_ranges(indices):
    """Groupe les indices consécutifs en ranges"""
    if not indices:
        return []
    
    ranges = []
    start = indices[0]
    end = indices[0]
    
    for i in range(1, len(indices)):
        if indices[i] == end + 1:
            end = indices[i]
        else:
            ranges.append((start, end))
            start = end = indices[i]
    
    ranges.append((start, end))
    return ranges

def image_to_glsl_custom_split(image_path, output_dir, split_x, compress=True):
    """
    Version avec point de séparation personnalisé
    """
    img = Image.open(image_path)
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    width, height = img.size
    
    colors_dict_left = {}
    colors_dict_right = {}
    
    for y in range(height):
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))
            
            if a != 255:
                continue
            
            pixel_index = y * width + x
            color_key = (r, g, b)
            
            if x < split_x:  # Partie gauche
                if color_key not in colors_dict_left:
                    colors_dict_left[color_key] = []
                colors_dict_left[color_key].append(pixel_index)
            else:  # Partie droite
                if color_key not in colors_dict_right:
                    colors_dict_right[color_key] = []
                colors_dict_right[color_key].append(pixel_index)
    
    create_glsl_file(colors_dict_left, os.path.join(output_dir, "logo_openmc_left.glsl"), "Left", compress)
    create_glsl_file(colors_dict_right, os.path.join(output_dir, "logo_openmc_right.glsl"), "Right", compress)
    
    print(f"Fichiers GLSL générés avec séparation à x = {split_x}")

# Exemple d'utilisation
if __name__ == "__main__":
    image_path = input("Chemin vers l'image : ")
    
    # Déterminer le dossier de sortie
    output_dir = os.path.dirname(image_path)
    if not output_dir:
        output_dir = "."
    
    # Choisir les options
    mode = input("Mode (1=milieu automatique, 2=position personnalisée) [1]: ").strip() or "1"
    compress = input("Compression (o/n) [o]: ").strip().lower() != "n"
    
    try:
        if mode == "2":
            split_x = int(input("Position de séparation (coordonnée x) : "))
            image_to_glsl_custom_split(image_path, output_dir, split_x, compress)
        else:
            image_to_glsl_split(image_path, output_dir, compress)
        
        print("Génération terminée avec succès !")
    except Exception as e:
        print(f"Erreur : {e}")