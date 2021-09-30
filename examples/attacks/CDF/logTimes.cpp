#include <cstdio>
#include <cstring>
#include <vector>
#include <string>

std::vector<std::string> readFileLines(const std::string& file){
  std::vector<std::string> result;
  std::string line;

  FILE *fp = fopen(file.c_str(), "r");

  if(!fp){
    printf("ERROR: Could not open file \"%s\"\n", file.c_str());
    exit(0);
  }

  while(!feof(fp)){
    char c = fgetc(fp);

    if(c == '\n'){
      if(line.size() >= 0){
        result.push_back(line);
      }
      line.clear();
    }
    else{
      line.push_back(c);
    }
  }
  if(line.size() > 1){
    result.push_back(line);
  }

  fclose(fp);

  return result;
}

double getTotalTime(const char* fileName){
  char buffer[256];
  char auxS[256];
  int auxI;
  char *ptr;

  std::vector<std::string> lines = readFileLines(fileName);

  sprintf(buffer, "%s", lines[0].c_str());

  ptr = strstr(buffer, ":") + 2;

  auxI = 0;
  while(*ptr != '\0'){
    auxS[auxI] = *ptr;
    auxI++;
    ptr++;
  }
  auxS[auxI] = '\0';
  double startTime = atof(auxS);

  sprintf(buffer, "%s", lines[lines.size() - 1].c_str());

  ptr = strstr(buffer, ":") + 2;

  auxI = 0;
  while(*ptr != '\0'){
    auxS[auxI] = *ptr;
    auxI++;
    ptr++;
  }
  auxS[auxI] = '\0';
  double endTime = atof(auxS);

  return (endTime - startTime) * 1000;
}

std::vector<int> getTimes(const std::string& folderPath){
  char buffer[256];

  const char files[10][16] = {"log5.txt", "log10.txt", "log15.txt", "log20.txt", "log25.txt", "log30.txt", "log35.txt", "log40.txt", "log45.txt", "log50.txt"};

  std::vector<int> times(10);

  for(int i = 0; i < 10; i++){
    sprintf(buffer, "%s/%s", folderPath.c_str(), files[i]);
    times[i] = getTotalTime(buffer);
  }

  for(int i = 1; i < 10; i++){
    int j = i - 1;
    while(j >= 0 && times[j] > times[j+1]){
      double aux = times[j];
      times[j] = times[j+1];
      times[j+1] = aux;

      j--;
    }
  }

  return times;
}

std::vector<int> merge(const std::vector<int>& t, const std::vector<int>& f){
  size_t i = 0, j = 0;

  std::vector<int> result(t.size() + f.size());

  while(i < t.size() && j < f.size()){
    if(t[i] < f[j]){
      result[i+j] = t[i];
      i++;
    }
    else{
      result[i+j] = f[j];
      j++;
    }
  }
  if(i == t.size()){
    while(j < f.size()){
      result[i+j] = f[j];
      j++;
    }
  }
  else{
    while(i < t.size()){
      result[i+j] = t[i];
      i++;
    }
  }

  return result;
}

bool isIn(const int v, const std::vector<int> vec){
  size_t i = 0;
  while(i < vec.size() && vec[i] != v)
    i++;
  return (i < vec.size());
}

void removeDups(std::vector<int>& v){
  for(int i = 0; i < (int) v.size() - 1; i++){
    if(v[i] == v[i+1]){
      v.erase(v.begin() + i + 1);
      i--;
    }
  }
}

int main(int argc, char* argv[]){

  std::vector<int> divisions(4);
  divisions[0] = 100;
  divisions[1] = 200;
  divisions[2] = 300;
  divisions[3] = 400;

  std::vector<int> vTrue = getTimes("Logs/vIFC-True");
  std::vector<int> vFalse = getTimes("Logs/vIFC-False");

  std::vector<int> merged = merge(vTrue, vFalse);
  removeDups(merged);

  FILE *fp = fopen("Plot/table.csv", "w");

  fprintf(fp, "Time;vIFC;No vIFC\n000;0.00;0.00\n");

  int tCount = 0, fCount = 0;

  for(size_t i = 0; i < merged.size(); i++){
    if(isIn(merged[i], vTrue))
      tCount++;
    if(isIn(merged[i], vFalse))
      fCount++;

    fprintf(fp, "%03d;%.2f;%.2f\n", merged[i], tCount / ((double) vTrue.size()),  fCount / ((double) vTrue.size()));
  }

  fclose(fp);
  printf("Table saved to: Plot/table.csv\n");

  return 0;
}
