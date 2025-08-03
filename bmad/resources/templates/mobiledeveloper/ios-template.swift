import UIKit
import SwiftUI

// UIKit Implementation
class MobileComponentViewController: UIViewController {
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "Mobile Component"
        label.font = UIFont.boldSystemFont(ofSize: 24)
        label.textColor = .label
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let actionButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Press Me", for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 10
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupConstraints()
    }
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        view.addSubview(titleLabel)
        view.addSubview(actionButton)
        
        actionButton.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)
    }
    
    private func setupConstraints() {
        NSLayoutConstraint.activate([
            titleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            titleLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor, constant: -50),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            
            actionButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            actionButton.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 30),
            actionButton.widthAnchor.constraint(greaterThanOrEqualToConstant: 120),
            actionButton.heightAnchor.constraint(equalToConstant: 50)
        ])
    }
    
    @objc private func buttonTapped() {
        print("Button tapped!")
        // Add your action here
    }
}

// SwiftUI Implementation
struct MobileComponentView: View {
    @State private var isDisabled = false
    
    var body: some View {
        VStack(spacing: 30) {
            Text("Mobile Component")
                .font(.title)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)
            
            Button(action: {
                print("Button tapped!")
            }) {
                Text(isDisabled ? "Disabled" : "Press Me")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(minWidth: 120, minHeight: 50)
                    .background(isDisabled ? Color.gray : Color.blue)
                    .cornerRadius(10)
            }
            .disabled(isDisabled)
        }
        .padding(20)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(.systemBackground))
    }
}

struct MobileComponentView_Previews: PreviewProvider {
    static var previews: some View {
        MobileComponentView()
    }
} 