using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CityMaker : MonoBehaviour
{
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;

    [SerializeField] GameObject turnPrefab1;
    [SerializeField] GameObject turnPrefab2;
    [SerializeField] GameObject turnPrefab3;
    [SerializeField] GameObject turnPrefab4;

    [SerializeField] GameObject interPrefab;
    public List<GameObject> buildingList;
    [SerializeField] GameObject destination;
    [SerializeField] GameObject semaphorePrefab;
    [SerializeField] int tileSize = 1;

    GameObject buildingPrefab;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        // Mesa has y 0 at the bottom
        // To draw from the top, find the rows of the file
        // and move down
        // Remove the last enter, and one more to start at 0
        int y = tiles.Split('\n').Length - 2;
        Debug.Log(y);

        Vector3 position;
        GameObject tile;

        for (int i=0; i<tiles.Length; i++) {
            if (tiles[i] == '>' || tiles[i] == '<') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'v' || tiles[i] == '^') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 's') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                tile = Instantiate(semaphorePrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'S') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                tile = Instantiate(semaphorePrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'D') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(destination, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == '#') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                buildingPrefab = buildingList[Random.Range(0, 3)];
                tile = Instantiate(buildingPrefab, position, Quaternion.identity);
                tile.transform.localScale = new Vector3(1, Random.Range(1f, 1.5f), 1);
                tile.transform.parent = transform;
                x += 1;
            }  else if (tiles[i] == 'x') {
                position = new Vector3(x * tileSize + 2, 0, y * tileSize - 2);
                tile = Instantiate(interPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.localScale = new Vector3(2, 1, 2);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '&') {
                position = new Vector3(x * tileSize + 2, 0, y * tileSize - 2);
                buildingPrefab = buildingList[Random.Range(0, 7)];
                tile = Instantiate(buildingPrefab, position, Quaternion.identity);
                tile.transform.localScale = new Vector3(2, 2, 2);
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '1') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(turnPrefab1, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '2') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(turnPrefab2, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '3') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(turnPrefab3, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '4') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(turnPrefab4, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            }
            else if (tiles[i] == '.') {
                x += 1;
            }
            else if (tiles[i] == '\n') {
                x = 0;
                y -= 1;
            }
        }

    }
}
