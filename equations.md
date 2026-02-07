$m$: vehicle mass including driver \
$\mu$: tire friction coefficient \
$r$: tire radius \
$G$: drive ratio \
$\eta$: drivetrain efficiency \
$C_d$: drag coefficient \
$A$: frontal area

---

$ F_{actual} = \min(F_{applied}, F_{traction}) $ 

$ F_{traction} = \mu F_n = \mu mg $ 

$ F_{applied} = F_{motor} - F_{resistance} $ 

$ F_{motor} = \frac{\tau_{engine} G \eta}{r} $ 

we get $\tau_{engine}$ from the motor torque curve (RPM vs torque)

calculate $ RPM = \frac{60Gv}{2\pi r}$ then map it to the MTC for $\tau_{engine}$ using linear interpolation

$ F_{resistance} = F_{drag} = \frac{1}{2} \rho C_d A v^2 $

---

$ \tau = Fr $ 

$ v = \omega r $ 




