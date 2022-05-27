use std::io::Read;
use std::process;
use std::fs;
use std::env;
fn main(){
  let argv: Vec<String> = env::args().collect();
  if argv.len() < 2{
    println!("Usage hexx <filename>");
    process::exit(1);
  }
  let filename = &argv[1];
  let mut fp = fs::File::open(filename).expect("Failed in opening file");

  let mut data: Vec<u8> = Vec::new();
  fp.read_to_end(&mut data).expect("Failed while reading file contents");

  println!("┌────────┬─────────────────────────┬─────────────────────────┬────────┬────────┐");
  
  let mut tmp: String;
  let mut i = 0;
  while i < data.len(){
    print!("│\x1b[36m{:08x}\x1b[0m│", i);

    for j in 0..16{
      if i + j >= data.len(){
        print!("   ");
      }
      else{
        match data[i + j]{
          0 => tmp = format!("\x1b[31m{:02x}\x1b[0m", data[i + j]),
          1..=32 => tmp = format!("\x1b[33m{:02x}\x1b[0m", data[i + j]),
          33..=126 => tmp = format!("\x1b[32m{:02x}\x1b[0m", data[i + j]),
          127..=255 => tmp = format!("\x1b[34m{:02x}\x1b[0m", data[i + j]),
        };
        print!(" {}", tmp);
      }
      if 7 == j{
        print!(" ┆");
      }
    }
    print!(" │");
    
    for j in 0..16{
      if (i + j) >= data.len(){
        print!(" ");
      }
      else{
        match data[i + j]{
          0 => tmp = "\x1b[31m⋄\x1b[0m".to_string(),
          1..=32 => tmp = "\x1b[33m•\x1b[0m".to_string(),
          33..=126 => tmp = format!("\x1b[32m{}\x1b[0m", char::from(data[i + j])),
          127..=255 => tmp = "\x1b[34m×\x1b[0m".to_string(),
        };

        print!("{}", tmp);
      }
      if 7 == j{
        print!("┆");
      }
    }

    println!("│");
    i += 16;
    // if 16 * 4 == i{
      // break;
    // }
  }
  println!("└────────┴─────────────────────────┴─────────────────────────┴────────┴────────┘");

}
