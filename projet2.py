#test avec sliders

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.widgets as wdg


#Définitions des variables
L = 1
Zc = 1.4
c = 340
w = 2*np.pi*300
k = w/c
x = np.linspace(-L,L,200)
Y = np.linspace(-0.5,0.5,50)

#Fonction permettant de recalculer les arrays de pression/vitesse en fonction des valeurs des sliders
def get_akoustik():
    """
    

    Returns
    -------
    pression : Numpy array
        Array de la pression en fonction de x.
    vitesse : Numpy array
        Array de la vitesse en fonction de x.

    """
    v1 = samp1.val*np.exp(1j*phase1.val)
    v2 = samp2.val*np.exp(1j*phase2.val)

    alpha = Zc/(2*1j*np.sin(2*k*L))
    A = alpha*(v1*np.exp(1j*k*L) - v2*np.exp(-1j*k*L)) 
    B = alpha*(v1*np.exp(-1j*k*L) - v2*np.exp(1j*k*L)) 

    pression = A*np.exp(-1j*k*x)+ B*np.exp(1j*k*x)
    vitesse = (A*np.exp(-1j*k*x) - B*np.exp(1j*k*x))/Zc
    
    return pression, vitesse



fig, ax = plt.subplots(2,1,figsize=(16,8))

#Définitions des sliders: positions/ valeurs
axamp = plt.axes([0.1, 0.96, 0.2, 0.03]) #Left, bottom, width, height
samp1 = wdg.Slider(axamp, 'Amp 1', 0, 1, valinit=1)
axamp2 = plt.axes([0.4, 0.96, 0.2, 0.03]) #Left, bottom, width, height
samp2 = wdg.Slider(axamp2, 'Amp 2', 0, 1, valinit=0)
axphase1 = plt.axes([0.1, 0.92, 0.2, 0.03]) #Left, bottom, width, height
phase1 = wdg.Slider(axphase1, 'phase 1', 0, np.pi, valinit=0)
axphase2 = plt.axes([0.4, 0.92, 0.2, 0.03]) #Left, bottom, width, height
phase2 = wdg.Slider(axphase2, 'phase 2', 0, np.pi, valinit=0)

mat_pression = np.zeros((len(x),50))
mat_vitesse = np.zeros((len(x),50))

def animate(i):
    """
    Retourne le tracé pour la fonction FuncAnimation

    Parameters
    ----------
    i : Integer
        Le numéro de l'image.

    Returns
    -------
    list
        Liste contenant les tracés.

    """

    image = 2*i/(600*300)
    
    pression, vitesse = get_akoustik()
    
    pression_reelle = np.real(pression*np.exp(1j*w*image))
    vitesse_reelle = np.real(vitesse*np.exp(1j*w*image))
    for j in range(mat_pression.shape[0]):
        mat_pression[j,:] = pression_reelle[j]
        mat_vitesse[j,:] = vitesse_reelle[j]
    
    trace = ax[0].pcolormesh(x,Y, np.transpose(mat_pression)[:-1, :-1],vmin=-1, vmax=1, cmap='RdBu')
    trace2 = ax[1].pcolormesh(x,Y, np.transpose(mat_vitesse)[:-1, :-1],vmin=-1, vmax=1, cmap='RdBu')
    
    return [trace, trace2]
        

ax[1].set_xlabel("Position dans le tube [m]")
ax[0].set_ylabel("Champs de pression")
ax[1].set_ylabel("Champs de vitesse")
    
ani = animation.FuncAnimation(fig, animate,frames = 300, interval = 50,repeat = True, blit=True)
#fig.colorbar(trace)   
#ani.save('anim.mp4')
plt.show()