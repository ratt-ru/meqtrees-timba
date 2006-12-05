# aips++/glish script to view an image created from a MS

func view(image_name){
    include 'image.g'
    myimage:=image(image_name)
    myimage.view();
}

if (len(argv)<=2){
    print "Usage:"
    print "glish viewImage.g IMAGE_NAME"; print ""
    exit
} else {
    view(argv[3])
}

