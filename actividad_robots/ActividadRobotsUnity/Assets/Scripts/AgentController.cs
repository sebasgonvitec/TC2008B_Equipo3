// TC2008B. Sistemas Multiagentes y Gr�ficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2021

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    public string id;
    public float x, y, z;
    public bool inStation;

    public AgentData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.inStation = false;
    }
}

[Serializable]

public class AgentsData
{
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getObstaclesEndpoint = "/getObstacles";
    string getStationsEndpoint = "/getStations";
    string getBoxesEndpoint = "/getBoxes";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData, stationData, boxData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    public GameObject agentPrefab, obstaclePrefab, floor, stationPrefab, boxPrefab;
    public int NAgents, width, height, box_num;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();
        stationData = new AgentsData();
        boxData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();

        floor.transform.localScale = new Vector3((float)width / 10, 1, (float)height / 10);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    private void Update()
    {
        if (timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

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

                agents[agent.Key].transform.localPosition = interpolated;
                //if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }

            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetBoxData());

        }
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());
        form.AddField("box_num", box_num.ToString());

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
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
            StartCoroutine(GetStationData());
            StartCoroutine(GetBoxData());
        }
    }

    IEnumerator GetAgentsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach (AgentData agent in agentsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);

                if (!started)
                {
                    prevPositions[agent.id] = newAgentPosition;
                    agents[agent.id] = Instantiate(agentPrefab, newAgentPosition, agentPrefab.transform.rotation);
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

    IEnumerator GetBoxData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxesEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            boxData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
          
            foreach (AgentData agent in boxData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
       
                if (!started)
                {
                    Debug.Log("Box Agent ID: " + agent.id);
                    prevPositions[agent.id] = newAgentPosition;
                    agents[agent.id] = Instantiate(boxPrefab, newAgentPosition, boxPrefab.transform.rotation);
                }
                else
                {
                    if(agent.inStation)
                    {
                        agents[agent.id].SetActive(false);
                        agents.Remove(agent.id);
                        currPositions.Remove(agent.id);
                        prevPositions.Remove(agent.id);
                    }
                    else
                    {
                        Vector3 currentPosition = new Vector3();
                        if (currPositions.TryGetValue(agent.id, out currentPosition))
                            prevPositions[agent.id] = currentPosition;
                        currPositions[agent.id] = newAgentPosition;
                    }
                }
            }

            updated = true;
            if (!started) started = true;
        }
    }

    IEnumerator GetObstacleData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getObstaclesEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            obstacleData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
            //Debug.Log(obstacleData.positions);

            foreach (AgentData obstacle in obstacleData.positions)
            {
                Instantiate(obstaclePrefab, new Vector3(obstacle.x, obstacle.y, obstacle.z), obstaclePrefab.transform.rotation);
            }
        }
    }

    IEnumerator GetStationData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getStationsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            stationData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            //Debug.Log(stationData.positions);

            foreach (AgentData station in stationData.positions)
            {
                Instantiate(stationPrefab, new Vector3(station.x, station.y, station.z), Quaternion.identity);
            }
        }
    }
}