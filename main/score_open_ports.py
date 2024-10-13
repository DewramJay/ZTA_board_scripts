

def score_calculation_openPorts(ports):
    # ports = []
    if ports:
        score_openPorts = 10

        critical_ports = [23,22]
        high_ports = [80, 8080, 443, 8443, 137, 139, 445]
        medium_ports = [161, 1883, 502, 1433, 1434, 3306]
        low_ports = [1900]
        critical_flag = True
        high_flag = True
        medium_flag = True
        low_flag = True

        for port in ports:
            for critical_port in critical_ports:
                if port == critical_port and critical_flag == True:
                    score_openPorts -= 4
                    critical_flag = False
                    break
            for high_port in high_ports:
                if port == high_port and high_flag == True:
                    score_openPorts -= 3
                    high_flag = False
                    break
            for medium_port in medium_ports:
                if port == medium_port and medium_flag == True:
                    score_openPorts -= 2
                    medium_flag = False
                    break
            for low_port in low_ports:
                if port == low_port and low_flag == True:
                    score_openPorts -= 1
                    low_flag = False
                    break
        score_openPorts=score_openPorts/10            
        print(score_openPorts)
        return score_openPorts
    else:
        return 1









# if __name__ == "__main__":
#     score_calculation_openPorts()