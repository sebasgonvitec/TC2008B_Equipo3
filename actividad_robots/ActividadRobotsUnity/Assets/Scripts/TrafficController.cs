
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;

[Serializable]
public class CarData // Class for agent data
{
    // Attributes
    public string id;
    public float x, y, z;

    public CarData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]
public class CarsData // agents data 
{
    public List<CarData> positions;

    public CarsData() => this.positions = new List<CarData>();

     public List<string> getCarIds()
    {
        List<string> res = new List<string>();

        foreach (CarData car in positions)
        {
            res.Add(car.id);
        }

        return res;
    }

}


[Serializable]
public class TrafficLight // Class for agent data
{
    // Attributes
    public string id;
    public float x, y, z;
    public string state;

    public TrafficLight(string id, float x, float y, float z, string state)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.state = state;

    }
}

[Serializable]
public class TrafficLights // agents data 
{
    public List<TrafficLight> trafficLightsList;

    public TrafficLights() => this.trafficLightsList = new List<TrafficLight>();
}


public class TrafficController : MonoBehaviour // Class agent controller
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    // Define variables 
    // Endpoints
    string serverUrl = "http://localhost:8585";
    string getCarsEndpoint = "/getCars";
    string getTrafficLightEndpoint = "/getTrafficLight";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    
    // Data instances
    CarsData carsData;
    TrafficLights trafficData;
    
    // Dictionaries for agents and positions
    Dictionary<string, GameObject> cars, trafficGreenLights, trafficRedLights;
    Dictionary<string, Vector3> prevPositions, currPositions;
    Dictionary<string, string> prevState;

    // Simulation states
    bool updated = false, started = false, finished = false;

    // Prefabs
    public List<GameObject> carList;
    public GameObject trafficGreenPrefab, trafficRedPrefab;
    GameObject carPrefab;

    // params
    public int NCars;
    // Time for simulation
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    // Initialize
    void Start()
    {
        // initialize data
        carsData = new CarsData();
        trafficData = new TrafficLights();

        // Positions dictionaries
        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        // agents dictionary
        cars = new Dictionary<string, GameObject>();
        
        trafficGreenLights = new Dictionary<string, GameObject>();
        trafficRedLights = new Dictionary<string, GameObject>();
        prevState = new Dictionary<string, string>();

        timer = timeToUpdate;
        // Send configuration coroutine
        StartCoroutine(SendConfiguration());
    }

    // update
    private void Update()
    {
         Debug.Log("Number of simultaneous cars: " + cars.Count);       

        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }
        // 
        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach (var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                cars[agent.Key].transform.localPosition = interpolated;
                if (direction != Vector3.zero) cars[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
            

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }

    // Update simulaton co routine 
    IEnumerator UpdateSimulation()
    {
        // Call endpoint
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
        // catch error
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        // If there is no error
        else
        {
            // Start coroutines
            StartCoroutine(GetTrafficLightsData());
            StartCoroutine(GetCarsData());
        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NCars", NCars.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetTrafficLightsData());
            StartCoroutine(GetCarsData());
           
        }
    }

    IEnumerator GetCarsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getCarsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            carsData = JsonUtility.FromJson<CarsData>(www.downloadHandler.text);

            List<string> carKeys = new List<string>(cars.Keys);

            foreach (string key in carKeys)
            {
                if(!carsData.getCarIds().Contains(key))
                {
                    Destroy(cars[key]);
                    cars.Remove(key);
                    prevPositions.Remove(key);
                    currPositions.Remove(key);
                }

            }

            foreach (CarData agent in carsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x * 4, agent.y, agent.z * 4 - 5);

                if (!prevPositions.ContainsKey(agent.id))
                {
                    prevPositions[agent.id] = newAgentPosition;
                    carPrefab = carList[UnityEngine.Random.Range(0,6)];
                    cars[agent.id] = Instantiate(carPrefab, newAgentPosition, carPrefab.transform.rotation);
                }
                else
                {
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(agent.id, out currentPosition))
                        prevPositions[agent.id] = currentPosition;
                    currPositions[agent.id] = newAgentPosition;
                }
            }
            updated = true;
        }
    }

    IEnumerator GetTrafficLightsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            trafficData = JsonUtility.FromJson<TrafficLights>(www.downloadHandler.text);
        
            foreach (TrafficLight agent in trafficData.trafficLightsList)
            {
                Vector3 newAgentPosition = new Vector3(agent.x * 4, agent.y, agent.z * 4 - 5);
            
                if (!trafficGreenLights.ContainsKey(agent.id))
                {
                    prevState[agent.id] = agent.state;

                    if(agent.state == "False"){
                        trafficRedLights[agent.id] = Instantiate(trafficRedPrefab, newAgentPosition, Quaternion.Euler(0, 90, 0));
                        trafficGreenLights[agent.id] = Instantiate(trafficGreenPrefab, newAgentPosition, Quaternion.Euler(0, 90, 0));
                        trafficGreenLights[agent.id].SetActive(false);
                    }   
                    else if(agent.state == "True"){
                        trafficRedLights[agent.id] = Instantiate(trafficRedPrefab, newAgentPosition, Quaternion.identity);
                        trafficGreenLights[agent.id] = Instantiate(trafficGreenPrefab, newAgentPosition, Quaternion.identity);
                        trafficRedLights[agent.id].SetActive(false);
                    }   
                }
                else
                {
                    if(prevState[agent.id] != agent.state && agent.state == "False"){
                        trafficGreenLights[agent.id].SetActive(false);
                        trafficRedLights[agent.id].SetActive(true);
                        prevState[agent.id] = agent.state;

                    }
                    else if(prevState[agent.id] != agent.state && agent.state == "True"){
                        trafficRedLights[agent.id].SetActive(false);
                        trafficGreenLights[agent.id].SetActive(true);
                        prevState[agent.id] = agent.state;

                    }
        
                }
            }
            // updated = true;
        }
    }

}

    