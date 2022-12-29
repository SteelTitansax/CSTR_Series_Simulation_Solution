#Libraries
import logging
import azure.functions as func
import json
import numpy as np
from scipy.integrate import solve_ivp


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Reactor designing Begins...')
        
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:

        volumen_A = req_body.get('volumen_A') #L
        volumen_B = req_body.get('volumen_B') #L
        f_A = req_body.get('f_A') #L/min
        f_B = req_body.get('f_B') #L/min
        f_Bout = req_body.get('f_Bout') #L/min
        trange = req_body.get('trange') #min

        
        #Parsing variables

        volumen_A = float(volumen_A) #L
        volumen_B = float(volumen_B) #L
        f_A = float(f_A) #L/min
        f_B = float(f_B) #L/min
        f_Bout = float(f_Bout)
        trange = float(trange) #min

        #Rest variables declaration

        concentracion_A0 = 550/volumen_A #g/l
        concentracion_B0 = 260/volumen_B #g/l

        print(f'A: {concentracion_A0} g/L')
        print(f'B: {concentracion_B0} g/L')

        c_A = 10 #g/L
        c_B = 30 #g/L
        f_AB = 3 #L/min
        f_BA = 1.5 #L/min
        
        print(f'Balance TA: {f_A + f_BA - f_AB} L/min')
        print(f'Balance TB: {f_B + f_AB - f_Bout} L/min')

        def dSdt(t,S):
            S_A = S[0]
            S_B = S[1]

            dSadt = ( f_A * c_A - f_AB * S_A + f_BA * S_B )/volumen_A
            dSbdt = ( f_B * c_B + f_AB * S_A - f_BA * S_B - f_Bout * S_B )/volumen_B

            return np.array([dSadt, dSbdt])


        S0 = (concentracion_A0, concentracion_B0)

        t_span = (0,trange) #min
        t_eval = np.linspace(t_span[0],t_span[1])

        sol = solve_ivp(dSdt, t_span, S0, t_eval = t_eval)


        # Consolidating outputs: 
        Ca = sol.y[0]
        Cb = sol.y[1]
        t = sol.t

        sol_json = []

        for item in range(50):

            sol_details = {
                        "Ca": Ca[item],
                        "Cb": Cb[item],
                        "t": t[item]
                    }

            sol_json.append(sol_details)

        logging.info(sol_json)

        return json.dumps(sol_json)
    
    return func.HttpResponse("Reactor design succesfully...",status_code=200)

