import numpy as np
import scipy.optimize as opt

def _sigmoid(z):
    return 1/(1 + np.e**(-z))

class LogReg:

    def __init__(self, num_features, num_labels, th=None,
                            reg_term=0.5, fun=_sigmoid):
        self.reg = reg_term
        self.fun = fun
        self.num_features = num_features
        self.num_labels = num_labels
        self.th = self._initial_thetas() if th is None else th

    def _initial_thetas(self):
        if self.num_labels == 2:
            return np.zeros(self.num_features+1)
        else:
            return np.zeros(self.num_labels, self.num_features+1)

    def _cost(self, params, x, y):
        """ Calcula el coste del modelo utilizando una funcion
        sigmoide.
        'params' es un argumento nulo, acoplado a sklearn.optimize,
        cualquier valor sirve(None), ya que no se utiliza.
        """
        m = len(x)
        h = self.fun(np.dot(x, self.th))
        
        J = np.sum( -y * np.log(h) - (1 - y) * np.log(1 - h) ) / m
        J += (self.reg / (2 * m)) * (np.sum(self.th ** 2))
        
        return J                         

    def _gradient(self, params, x, y):
        """ Calcula el gradiente del modelo utilizando una funcion
        sigmoide.
        'params' es un argumento nulo, acoplado a sklearn.optimize,
        cualquier valor sirve(None), ya que no se utiliza.
        """ 
        m = len(x)
        cg = (1/m)*x.T.dot(self.fun(np.dot(x, self.th)) - y) + self.th*self.reg/m
        return cg

    def fit(self, X, y):
        """
        Entrena los pesos del modelo utilizando 'fmin_tnc' de 
        la libreria 'scipy.optimize'
        """
        m = len(X)
        X_ones = np.insert(X, 0,values=np.ones(m), axis=1)
        if self.num_labels == 2:
            self.th, *ret = opt.fmin_tnc(func=self._cost, x0=self.th, 
                       fprime=self._gradient, args=(X_ones, y), maxfun=100)
            print(f'num_func_eval:{ret[0]}')
        else:
            # equivalente a oneVsAll()
            for i in range(1, self.num_labels + 1):
                self.th[i], *ret  = opt.fmin_tnc(func=self._cost, x0=self.th[i],
                                    fprime=self._gradient, args=(X_ones, y))
                print(f'label:{i}, num_func_eval:{ret[0]}')

    def predict(self, X, threshold=0.5):
        """ Devuelve las predicciones del modelo para los datos
        de 'X' utilizando 'threshold' si el modelo solo
        tiene dos posibles etiquetas
        """
        m = len(X)
        X_ones = np.insert(X, 0,values=np.ones(m), axis=1)
        pred = []
        for x in X_ones:
            if(self.num_labels == 2):
                prediction = self.fun(self.th.dot(x.T))
                if(prediction >= threshold):
                    prediction = 1
                else:
                    prediction = 0
            else:
                probability_per_classifier = np.array([self.fun(self.th[i].dot(x.T)) 
                                                for i in range(0,self.num_labels)])
                best_probability_prediction_index = np.argmax(probability_per_classifier)
                prediction = best_probability_prediction_index+1
            
            pred.append(prediction)
        return np.array(pred)

    def accuracy_score(self, y_true, y_pred, normalize=True):
        """ Calcula el porcentaje de aciertos del modelo sobre 'y_true'
        utilizando las predicciones de 'y_pred'
        Si 'normalize'=False, devuelve el numero de aciertos
        """
        assert len(y_true) == len(y_pred)
    
        num_hits = 0
        m = len(y_true)
        for i in range(0,m):
            if(y_true[i] == y_pred[i]):
                num_hits += 1

        return (num_hits/m)*100 if normalize else num_hits