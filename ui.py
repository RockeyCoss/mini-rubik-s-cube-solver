import vpython as vp

vp.scene.width=700
vp.scene.height=700

faces={
    'red':(vp.color.red,(1,0,0)),
    'blue':(vp.color.blue,(0,0,1)),
    'yellow':(vp.color.yellow,(0,1,0)),
    'white':(vp.color.white,(0,-1,0)),
    'orange':(vp.color.orange,(-1,0,0)),
    'green':(vp.color.green,(0,0,-1))
}
squares=[]
for color, normalVector in faces.values():
    for x in (-0.5,0.5):
        for y in (-0.5,0.5):
            square=vp.box(color=color,pos=vp.vector(x,y,1),length=0.98,height=0.98,width=0.05)
            cosine=vp.dot(vp.vector(0,0,1),vp.vector(*normalVector))
            axis=(vp.cross(vp.vector(0,0,1),vp.vector(*normalVector))
                  if cosine==0 else vp.vector(1,0,0))
            square.rotate(angle=vp.acos(cosine),origin=vp.vector(0,0,0),axis=axis)
            squares.append(square)
    vp.scene.lights.append(vp.distant_light(direction=vp.vector(*normalVector),color=vp.color.gray(0.3)))

operations=['R',"R'","U","U'","F","F'","D","D'","L","L'","B","B'"]
for operation in operations:

