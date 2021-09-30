#include <cstdio>
#include <cstring>
#include <vector>
#include <string>

int intFromString(char str[]){
  int result = 0;

  int i = 0;
  while(str[i] != '\0'){
    if(str[i] >= '0' && str[i] <= '9'){
      result = result * 10 + (str[i] - '0');
    }
    else{
      return 0;
    }
    i++;
  }

  return result;
}

std::string toHex(const int n){
  const char cs[16] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'};

  std::string result;

  if(n <= 0 || n > 255)
    result = "00";
  else{
    result.push_back(cs[n/16]);
    result.push_back(cs[n%16]);
  }

  return result;
}

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

void parseArgs(const int argc, char *argv[], bool *help, int *switchCount){
  int i = 1;
  while(i < argc){
    if(!strcmp(argv[i], "-s") || !strcmp(argv[i], "--switches")){
      i++;
      if(i < argc){
        *switchCount = intFromString(argv[i]);
        if(*switchCount < 0){
          printf("Error - Invalid switch count: %s\n", argv[i]);
          exit(0);
        }
      }
    }
    else if(!strcmp(argv[i], "-h") || !strcmp(argv[i], "--help")){
      *help = true;
    }

    i++;
  }
}

void showHelp(){
  printf("Usage: ./createExp [ARGS]\n\n");
  printf("Args:\n");
  printf("(-h | --help)       : Displays help message\n");
  printf("(-s | --switches) N : Set switch count\n");
}

void createTopoFile(const int switchCount){
  FILE *topoFile = fopen("Mininet/topology.json", "w");

  fprintf(topoFile, "{\n\t\"hosts\": {\n");
  fprintf(topoFile, "\t\t\"h1\": {\"ip\": \"10.0.1.1/24\", \"mac\": \"08:00:00:00:00:01:01\",\n");
  fprintf(topoFile, "\t\t\t\"commands\":[\"route add default gw 10.0.1.0 dev eth0\",\n");
  fprintf(topoFile, "\t\t\t            \"arp -i eth0 -s 10.0.1.0 08:00:00:00:01:00\",\n");
  fprintf(topoFile, "\t\t\t            \"arp -i eth0 -s 10.0.1.2 08:00:00:00:02:02\"]},\n");
  fprintf(topoFile, "\t\t\"h2\": {\"ip\": \"10.0.1.2/24\", \"mac\": \"08:00:00:00:00:02:02\",\n");
  fprintf(topoFile, "\t\t\t\"commands\":[\"route add default gw 10.0.1.0 dev eth0\",\n");
  fprintf(topoFile, "\t\t\t            \"arp -i eth0 -s 10.0.1.0 08:00:00:00:02:00\",\n");
  fprintf(topoFile, "\t\t\t            \"arp -i eth0 -s 10.0.1.1 08:00:00:00:01:01\"]}\n\t},\n");
  fprintf(topoFile, "\t\"switches\": {\n");

  for(int i = 0; i < switchCount + 1; i++){
    fprintf(topoFile, "\t\t\"s%d\": { \"runtime_json\": \"s%d-runtime.json\" }", i+1, i+1);

    if(i < switchCount)
      fprintf(topoFile, ",\n");
  }

  fprintf(topoFile, "\n\t},\n\t\"links\": [\n");
  fprintf(topoFile, "\t\t[\"h1\", \"s1-p1\"], [\"h2\", \"s1-p2\"],\n\t\t");

  for(int i = 0; i < switchCount; i++){
    fprintf(topoFile, "[\"s1-p%d\", \"s%d-p1\"]", i + 3, i + 2);
    if(i < switchCount - 1)
      fprintf(topoFile, ", ");
  }

  fprintf(topoFile, "\n\t]\n}\n");

  fclose(topoFile);
}

void createS1RuntimeSwitchJson(const int switchCount){
  FILE *fp = fopen("Mininet/s1-runtime.json", "w");

  fprintf(fp, "{\n\t\"target\": \"bmv2\",\n\t\"p4info\": \"build/l2.p4.p4info.txt\",\n");
  fprintf(fp, "\t\"bmv2_json\": \"build/l2.json\",\n");
  fprintf(fp, "\t\"table_entries\": [\n\t\t{\n");
  fprintf(fp, "\t\t\t\"table\": \"MyIngress.dmac\",\n\t\t\t\"match\": {\n");
  fprintf(fp, "\t\t\t\t\"hdr.ethernet.dstAddr\": \"08:00:00:00:01:01\"\n\t\t\t},\n");
  fprintf(fp, "\t\t\t\"action_name\": \"MyIngress.set_out_port\",\n\t\t\t\"action_params\": {\n");
  fprintf(fp, "\t\t\t\t\"port\": 1\n\t\t\t}\n\t\t},\n\t\t{\n");
  fprintf(fp, "\t\t\t\"table\": \"MyIngress.dmac\",\n\t\t\t\"match\": {\n");
  fprintf(fp, "\t\t\t\t\"hdr.ethernet.dstAddr\": \"08:00:00:00:02:02\"\n\t\t\t},\n");
  fprintf(fp, "\t\t\t\"action_name\": \"MyIngress.set_out_port\",\n\t\t\t\"action_params\": {\n");
  fprintf(fp, "\t\t\t\t\"port\": 2\n\t\t\t}\n\t\t},\n");

  for(int i = 0; i < switchCount; i++){
    fprintf(fp, "\t\t{\n\t\t\t\"table\": \"MyIngress.dmac\",\n\t\t\t\"match\": \{\n");
    fprintf(fp, "\t\t\t\t\"hdr.ethernet.dstAddr\": \"08:00:00:00:01:%s\"\n\t\t\t},\n", toHex(i + 3).c_str());
    fprintf(fp, "\t\t\t\"action_name\": \"MyIngress.set_out_port\",\n\t\t\t\"action_params\": {\n\t\t\t\t\"port\": %d\n\t\t\t}\n\t\t}", i+3);

    if(i < switchCount - 1)
      fprintf(fp, ",\n");
  }

  fprintf(fp, "\n\t]\n}\n");

  fclose(fp);
}

void createSwitchesRuntimeSwitchJson(const int switchCount){
  char buffer[256];

  for(int i = 0; i < switchCount; i++){
    sprintf(buffer, "Mininet/s%d-runtime.json", i+2);
    FILE *fp = fopen(buffer, "w");

    fprintf(fp, "{\n\t\"target\": \"bmv2\",\n\t\"p4info\": \"build/l2.p4.p4info.txt\",\n");
    fprintf(fp, "\t\"bmv2_json\": \"build/l2.json\",\n\t\"table_entries\": [\n");
    fprintf(fp, "\t\t{\n\t\t\t\"table\": \"MyIngress.checkCPU\",\n\t\t\t\"match\": {\n\t\t\t\t\"hdr.ethernet.dstAddr\": \"08:00:00:00:01:%s\"\n", toHex(i + 3).c_str());
    fprintf(fp, "\t\t\t},\n\t\t\t\"action_name\": \"MyIngress.send_to_cpu\",\n\t\t\t\"action_params\": {\n\t\t\t\t\"s_id\": %d\n\t\t\t}\n\t\t}\n\t]\n}", i+2);

    fclose(fp);
  }
}

void createRunExercise(const int switchCount){
  char buffer[256];

  std::vector<std::string> lines = readFileLines("Mininet/utils/run_exercise.py.tmp");

  for(int i = 0; i < switchCount; i++){
    sprintf(buffer, "\tIntf('enp0s3', node=self.net.getNodeByName(\"s%d\"), port=255)", i + 2);
    lines.insert(lines.begin() + 210 + i, std::string(buffer));
  }

  FILE *fp = fopen("Mininet/utils/run_exercise.py", "w");

  for(std::string line : lines)
    fprintf(fp, "%s\n", line.c_str());

  fclose(fp);
}

void createLoadVSwitch(const int switchCount){
  FILE *fp = fopen("LoadVSwitch.py", "w");

  fprintf(fp, "import os\n\nfrom utils.SM_mgmt import *\nfrom config.PermEnum import *\nfrom config.SwitchTypeEnum import *\n\n");
  fprintf(fp, "class LoadVSwitch():\n\n\t@staticmethod\n\tdef load_switches():\n");
  fprintf(fp, "\t\tSM_mgmt.init_database()\n\t\tSM_mgmt.load_libsume_module(\"platform_api/lib/hwtestlib/libsume.so\")\n\n");

  fprintf(fp, "\t\tAuth.addUser(\"ivan1\", \"ivan1\")\n");
  fprintf(fp, "\t\tAuth.addUser(\"admin\", \"admin\")\n");

  fprintf(fp, "\n\t\tswitch_id = 1\n");

  for(int i = 0; i < switchCount + 1; i++){
    fprintf(fp, "\n\t\tif (SwitchConf.getSwitchById(switch_id) == False):\n");
    fprintf(fp, "\t\t\tprint \"Loading s%d\"\n", i+1);
    fprintf(fp, "\t\t\tSM_mgmt.create_switch_data(switch_id, \"l2-%d\", TYPE_BMV2, \"\", \"\", bmv2_address=\"127.0.0.1:50%03d\")\n", i+1, i+52);

    if(i == 0)
      fprintf(fp, "\n\t\t\tAuth.addPermission(\"ivan1\", \"l2-1\", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)");

    fprintf(fp, "\n\t\t\tAuth.addPermission(\"admin\", \"l2-%d\", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)\n", i+1);
    fprintf(fp, "\n\t\tswitch_id += 1\n");
  }

  fclose(fp);
}

void createClientTrigger(const int switchCount){
  char buffer[256];
  sprintf(buffer, "    switch_count = %d", switchCount);

  std::vector<std::string> lines = readFileLines("TriggerApp/client_trigger.py");

  lines[121] = std::string(buffer);

  FILE *fp = fopen("TriggerApp/client_trigger.py", "w");

  for(std::string line : lines)
    fprintf(fp, "%s\n", line.c_str());

  fclose(fp);
}

int main(int argc, char* argv[]){
  bool help = (argc <= 1);
  int switchCount = 3;

  parseArgs(argc, argv, &help, &switchCount);

  if(help){
    showHelp();
    return 0;
  }

  createTopoFile(switchCount);
  createS1RuntimeSwitchJson(switchCount);
  createSwitchesRuntimeSwitchJson(switchCount);
  createRunExercise(switchCount);
  createLoadVSwitch(switchCount);
  createClientTrigger(switchCount);

  return 0;
}
