import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.widgets as wdg


class tube_oscillant:
    def __init__(self, figure = None, w_size = (14,8), N = 200, L=1, Zc = 1.4):
        """
        Méthode d'initialisation de l'instance

        Parameters
        ----------
        figure : Tuple, optional
            Figure matplotlib
        w_size : tube, optional
            Taille de la figure
        N : Int, optional
            Nombres d'images pour une période
        L : Int, optional
            Demie longueur du tube
        Zc : float, optional
            Impédance du milieu fluide

        Returns
        -------
        None.

        """
        #Si aucune figure n'est spécifiée, on créer une figure
        if figure != None:
            self.fig, self.ax = figure
        else:
            self.fig, self.ax = plt.subplots(2,1,figsize=w_size)
        self.N = N #Nombre d'image pour une période    
        self.L = L #Longueur du tube
        self.Zc = Zc #Impédance du milieu
        self.c = 340 # célérité du son
        
        self.x = np.linspace(-self.L,self.L,200) #Vecteur x correspondant à la longueur du tube
        self.Y = np.linspace(-0.5,0.5,50) #Vecteur Y correspondant à la largeur du tube

        self.__init_figure()
        
        
    def __init_figure(self):
        """
        Initialisation de la figure: créations des sliders, limites, labels...

        Returns
        -------
        None.

        """
        #Création des axes des sliders: positions
        self.axamp = plt.axes([0.1, 0.96, 0.2, 0.03]) #Left, bottom, width, height
        self.axamp2 = plt.axes([0.4, 0.96, 0.2, 0.03])
        self.axphase1 = plt.axes([0.1, 0.92, 0.2, 0.03])
        self.axphase2 = plt.axes([0.4, 0.92, 0.2, 0.03])
        self.axfreq = plt.axes([0.7, 0.96, 0.2, 0.03])
        self.axperte = plt.axes([0.7, 0.92, 0.2, 0.03])
        
        #Création des sliders
        self.samp1 = wdg.Slider(self.axamp, 'Amp 1', 0, 1, valinit=1)
        self.samp2 = wdg.Slider(self.axamp2, 'Amp 2', 0, 1, valinit=0)
        self.phase1 = wdg.Slider(self.axphase1, 'phase 1', 0, np.pi, valinit=0)
        self.phase2 = wdg.Slider(self.axphase2, 'phase 2', 0, np.pi, valinit=0)
        self.perte = wdg.Slider(self.axperte, "Pertes", 0,1, valinit = 0)
        self.freq = wdg.Slider(self.axfreq, 'Fréquence', 100, 500, valinit=300)
         
        #Labels + titres + xticks
        self.ax[1].set_xlabel("Position dans le tube [m]")
        self.ax[0].set_title("Champs de pression")
        self.ax[1].set_title("Champs de vitesse particulaire")
        self.ax[0].set_xlim(-self.L-0.1,self.L+0.1)
        self.ax[1].set_xlim(-self.L-0.1,self.L+0.1)
        plt.setp(self.ax, xticks=[-self.L, 0, self.L], xticklabels=['-L', '0', 'L'])
        
        #On plot une première fois le champ de pression/vitesse, on indique ici les options (couleurs, line_width etc...)
        pression, vitesse, w = self.get_akoustik()
        pression_reelle = np.real(pression)
        vitesse_reelle = np.real(vitesse)

        #On "copie-colle" la pression et la vitesse pour créer un array 2D
        self.mat_pression = np.tile(pression_reelle,(50,1))
        self.mat_vitesse = np.tile(vitesse_reelle,(50,1))
            
        #Plot des champs
        self.quad_pression = self.ax[0].pcolormesh(self.x,self.Y, self.mat_pression[:-1, :-1],vmin=-1.5, vmax=1.5, cmap='coolwarm')
        self.quad_vitesse = self.ax[1].pcolormesh(self.x,self.Y, self.mat_vitesse[:-1, :-1],vmin=-1.5, vmax=1.5, cmap='coolwarm')

        self.HP1, = self.ax[0].plot([], lw = 5, color ="k")
        self.HP2, = self.ax[0].plot([], lw=5, color ="k")
        
        #Création de la colorbar pour l'échelle
        ax_colorbar = plt.axes([0.92, 0.1, 0.04, 0.8]) #Left, bottom, width, height
        self.fig.colorbar(self.quad_pression,ax_colorbar) 
        
    def get_akoustik(self):
        """
        Fonction permettant de recalculer les arrays de pression/vitesse en 
        fonction des valeurs des sliders

        Returns
        -------
        pression : Numpy array
            Array de la pression en fonction de x.
        vitesse : Numpy array
            Array de la vitesse en fonction de x.
        w : float
            pulsation des haut-parleurs

        """
        
        w = 2*np.pi*self.freq.val #On calcule la pulsation (elle n'a peut être pas changé, mais au moins on est sûr)
        k =(w/self.c)*(1- 1j*self.perte.val) #On calcule le nombre d'onde complexe, si le slider perte = 0, k = w/c
        
        #On définit les vitesses des pistons (amplitude + phase)
        v1 = self.samp1.val*np.exp(1j*self.phase1.val)
        v2 = self.samp2.val*np.exp(1j*self.phase2.val)

        #On calcule les amplitudes complexes du champ
        alpha = self.Zc/(2*1j*np.sin(2*k*self.L))
        A = alpha*(v1*np.exp(1j*k*self.L) - v2*np.exp(-1j*k*self.L)) 
        B = alpha*(v1*np.exp(-1j*k*self.L) - v2*np.exp(1j*k*self.L)) 
        
        #Calcul des champs
        pression = A*np.exp(-1j*k*self.x)+ B*np.exp(1j*k*self.x)
        vitesse = (A*np.exp(-1j*k*self.x) - B*np.exp(1j*k*self.x))/self.Zc
        
        return pression, vitesse, w
    
    def animate(self,i):
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
        #On récupère les champs de pression et vitesse
        pression, vitesse, w = self.get_akoustik()
        
        #Calcul du vecteur t en fonction de la fréquence, de manière à afficher une période complète
        t = np.linspace(0,1/(w/(2*np.pi)),self.N)

        #Calcul des champs réels
        pression_reelle = np.real(pression*np.exp(1j*w*t[i]))
        vitesse_reelle = np.real(vitesse*np.exp(1j*w*t[i]))

        #On "copie-colle" la pression et la vitesse pour créer un array 2D
        self.mat_pression = np.tile(pression_reelle,(50,1))
        self.mat_vitesse = np.tile(vitesse_reelle,(50,1))
        
        #On change les valeurs du pcolormesh
        self.quad_pression.set_array(self.mat_pression[:-1, :-1].ravel())
        self.quad_vitesse.set_array(self.mat_vitesse[:-1, :-1].ravel())
        
        #On change la positions des haut-parleurs
        self.HP1.set_data([(self.samp1.val*np.sin(w*t[i]+self.phase1.val)/(20))-self.L,(-0.5,0.5)])
        self.HP2.set_data([(self.samp2.val*np.sin(w*t[i]+self.phase2.val)/(20))+self.L,(-0.5,0.5)])
        
        return [self.quad_pression,self.quad_vitesse, self.HP1, self.HP2]
    
    #méthode qui lance l'animation
    def animation(self):
        self.ani = animation.FuncAnimation(self.fig, self.animate,frames = self.N, interval = 10,repeat = True, blit=True)  
        plt.show()
 
#Exemple 1
if __name__ == "__main__":
    #Petit exemple, qui ne s'éxécute seulement si on lance ce fichier directement
    exemple = tube_oscillant()
    exemple.animation()
    
    
#Exemple 2 avec une figure spécifiée comportant un plot
# if __name__ == "__main__":
#     fig_test = plt.subplots(3,1,figsize =(14,7)) 
    
#     x = np.linspace(-1,1,100)
#     y = np.cos(10*x)
#     fig_test[1][2].plot(x,y)
    
    
#     exemple = tube_oscillant(figure = fig_test)
#     exemple.animation()