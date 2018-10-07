
def refactor_image_name(image_name):
    def tuofeng(x):
        if len(x) > 1:
            return x[0].upper()+x[1:]
        else:
            return x

    name_list = image_name.split('_')
    if len(name_list) > 1:
        names = map(tuofeng, image_name.split('_')[1:])
        return image_name.split('_')[0][0].lower()+image_name.split('_')[0][1:]+''.join(list(names))
    else:
        return image_name[0].lower() +image_name[1:]
        