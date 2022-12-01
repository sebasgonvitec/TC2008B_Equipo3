
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

public class TrafficController : MonoBehaviour // Class agent controller
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    // Define variables 
    // Endpoints
    string serverUrl = "http://localhost:8585";
    string getCarsEndpoint = "/getCars";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    
    // Data instances
    CarsData carsData;
    
    // Dictionaries for agents and positions
    Dictionary<string, GameObject> cars;
    Dictionary<string, Vector3> prevPositions, currPositions;

    // Simulation states
    bool updated = false, started = false, finished = false;

    // Prefabs
    public List<GameObject> carList;
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

        // Positions dictionaries
        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        // agents dictionary
        cars = new Dictionary<string, GameObject>();

        timer = timeToUpdate;
        // Send configuration coroutine
        StartCoroutine(SendConfiguration());
    }

    // update
    private void Update()
    {
        
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
                Vector3 newAgentPosition = new Vector3(agent.x * 4, agent.y, agent.z * 4);

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

}

    