#**Final Project PR Spring 2020**
##**Monte Carlo Simulation on Hospital Capacity during COVID-19**

##**Team Members- Rohit Sanvaliya, Tanya Gupta, Varad Deshpande**

###**The need for this project from the perspective of hospitals**
COVID-19 came into this world without any warning or signs. This unannounced global pandemic was something the hospitals weren't prepared for and has called for crisis management measures. The hospitals have to make do with the available resources and make sure that there is maximum utilization of these resources to test and treat the patients that need urgent care. Our project witnesses a model called the SEIR model (Susceptible-Exposed-Infected-Result model) inspired from the SEIR model (Susceptible-Exposed-Infected-Recovered model). In our model, the R stands for result which includes people who are recovering as well as dying from COVID-19 compared to the R in the original SEIR model which stands for just the people who have recovered. Our model considers the various aspects of COVID-19, the statistics and data related to these aspects and then simulates the possibility of hospital beds overflowing for a fixed population and a fixed number of beds for a given number of days. This can prove to be helpful for hospitals in planning, managing and foreseeing the utilization of resources in these trying times enabling the healthworkers to drive their attention towards enhancing the diagnosis of the COVID-19 patients.

###**Model for the simulation**
SEIR model is a compartmental model where each compartment dentots the number of people in that compartment. 
The model is as follows: S-𝛽->E-𝛼->I-𝛾->R
We have fit suitable variables in the model and altered the calculations for each transitional variable to get accurate results.

Susceptible (S): 100% of the population is Susceptible to COVID-19
Exposed (E): Number of people who has contracted the virus. We considered the social distancing and incubation rate (5%) of the Exposed
Infected (I): Total population exposed to the virus and got Infection
Result (R): Patients who has vacated the hospital bed either by recovery or death


###**Simulation Variables**
Infectious Rate (𝛽) = 𝑅_1* 𝛾  (𝑅_1 – Reproduction Rate when social distancing is followed, 𝛾 – Recovery Rate)
Incubation Rate (𝛼) = 1/Incubation Period (Incubation Period – The duration after which the patients show symptoms after being exposed)
Recovery Rate (𝛾) = 1/Infectious Period (Infectious Period – The duration in which the patient is capable of spreading COVID-19)
Arrival Rate of people to be tested – The rate at which potential infected people are arriving in the hospital
Probability of people testing positive for COVID-19 – Positive specimens out of the total specimens tested
Service time distribution of testing kits – The time taken to receive test results for COVID-19
Time to outcome - It is the time taken by patients to get either recover or for their unfortunate death

###**Assumptions or Starting state for the Model**
Fixed number of hospital beds
Fixed population around the hospital
Zero COVID-19 patients in the hospital
Hospital can accommodate any arrival rate 
Social distancing is followed at its fullest
Testing kits used are 100% accurate
Recovered patients are not getting re-infected

###**Compartmental Equations**
Each compartment in the our model gives the number of people in that compartment
Our inspired model has the following compartment definitions – 
Susceptible_𝑛 = Susceptibl_(𝑛−1) - (𝛽*Infected_(𝑛−1)* Susceptible_(𝑛−1))
Exposed_𝑛 = (Exposed_(𝑛−1)- (𝛼* Exposed_(𝑛−1)))*0.05  +
Infected_𝑛 = (Arrival Rate of people to be tested* Probability of people testing positive for COVID-19* Exposed_𝑛)
Hospitalized_𝑛 = 0.17* Infected_𝑛  ++
Result_𝑛 = 𝛾* Hospitalized_𝑛

+ The value 0.05 is the probability that people will come in contact with each other despite social distancing
++ The value 0.17 is the probability of the total infected people being hospitalized

##**Hypotheses**##

###**Hypothesis-1**
If the number of hospital beds is doubled, there will never be an overflow.
Our analysis is conducted on the Chicago area with population of 2.71 million and number of hospital beds to be around 33000.
Using this we ran simulations 10000 times to test the hypothesis.
Test-1: Before doubling the number of beds
The following plot shows the simulation results depecting how beds in hospitals are occupied and how they will overflow after certain time.
![Alt text](C:\Users\clustervarad\Desktop\Sem II\IS590 PR\Final Project\Plots\Hypothesis -1 Plots\beds-vs-days.png?raw=true "Available beds vs Days")

The following plot shows on which day the hospitals are most probable of getting overflow.
![Alt text](C:\Users\clustervarad\Desktop\Sem II\IS590 PR\Final Project\Plots\Hypothesis -1 Plots\overflow-days-hist.png?raw=true "Day on which the hospitals overflow")
Test-2: After Doubling the number of beds

The following plot shows the number of available beds once they are doubled
![Alt text](C:\Users\clustervarad\Desktop\Sem II\IS590 PR\Final Project\Plots\Hypothesis -1 Plots\After\beds-vs-days.png?raw=true "Available beds vs Days")

The following plot gives the available number of vacant beds in the hospitals
![Alt text](C:\Users\clustervarad\Desktop\Sem II\IS590 PR\Final Project\Plots\Hypothesis -1 Plots\After\percent_vacant_beds-hist.png?raw=true "Percent Vacant Beds")










